# Terraform configuration for PayLabs Merchant Health Intelligence Platform
# Deploys infrastructure on Alibaba Cloud

terraform {
  required_providers {
    alicloud = {
      source  = "aliyun/alicloud"
      version = "~> 1.240.0"
    }
  }
  required_version = ">= 1.0.0"
}

provider "alicloud" {
  access_key = var.alicloud_access_key
  secret_key = var.alicloud_secret_key
  region     = var.alicloud_region
}

# Variables
variable "alicloud_access_key" {
  description = "Alibaba Cloud Access Key ID"
  type        = string
  sensitive   = true
}

variable "alicloud_secret_key" {
  description = "Alibaba Cloud Secret Key"
  type        = string
  sensitive   = true
}

variable "alicloud_region" {
  description = "Alibaba Cloud Region"
  type        = string
  default     = "ap-southeast-1"  # Singapore (closest to Indonesia)
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "paylabs-merchant-health"
}

variable "environment" {
  description = "Environment (dev/staging/prod)"
  type        = string
  default     = "dev"
}

# Resource naming locals
locals {
  name_prefix = "${var.project_name}-${var.environment}"
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# VPC Network
resource "alicloud_vpc" "main" {
  vpc_name   = "${local.name_prefix}-vpc"
  cidr_block = "10.0.0.0/16"
}

# VSwitch for ECS and RDS
resource "alicloud_vswitch" "main" {
  vpc_id       = alicloud_vpc.main.id
  cidr_block   = "10.0.1.0/24"
  zone_id      = "${var.alicloud_region}a"
  vswitch_name = "${local.name_prefix}-vswitch"
}

# Security Group for ECS
resource "alicloud_security_group" "ecs" {
  name   = "${local.name_prefix}-ecs-sg"
  vpc_id = alicloud_vpc.main.id
}

resource "alicloud_security_group_rule" "ecs_http" {
  security_group_id = alicloud_security_group.ecs.id
  ip_protocol       = "tcp"
  port_range        = "8000/8000"
  cidr_ip           = "0.0.0.0/0"
  policy            = "accept"
  type              = "ingress"
}

resource "alicloud_security_group_rule" "ecs_ssh" {
  security_group_id = alicloud_security_group.ecs.id
  ip_protocol       = "tcp"
  port_range        = "22/22"
  cidr_ip           = "0.0.0.0/0"
  policy            = "accept"
  type              = "ingress"
}

# Security Group for RDS
resource "alicloud_security_group" "rds" {
  name   = "${local.name_prefix}-rds-sg"
  vpc_id = alicloud_vpc.main.id
}

resource "alicloud_security_group_rule" "rds_mysql" {
  security_group_id = alicloud_security_group.rds.id
  ip_protocol       = "tcp"
  port_range        = "3306/3306"
  cidr_ip           = "10.0.0.0/16"  # Allow from VPC only
  policy            = "accept"
  type              = "ingress"
}

# ECS Instance for Backend
resource "alicloud_instance" "backend" {
  instance_name        = "${local.name_prefix}-backend"
  availability_zone    = "${var.alicloud_region}a"
  security_groups      = [alicloud_security_group.ecs.id]
  instance_type        = "ecs.g6.large"  # 2 vCPU, 8GB RAM
  image_id             = "ubuntu_22_04_x64_202312_20G_alibase_20240105.vhd"
  system_disk_category = "cloud_efficiency"
  system_disk_size     = 40
  vswitch_id           = alicloud_vswitch.main.id
  internet_max_bandwidth_out = 10

  tags = local.common_tags

  user_data = <<-EOF
              #!/bin/bash
              # Install Docker
              apt-get update
              apt-get install -y docker.io docker-compose
              systemctl enable docker
              systemctl start docker

              # Install Python
              apt-get install -y python3 python3-pip
              EOF
}

# Elastic IP for ECS
resource "alicloud_eip" "backend" {
  name            = "${local.name_prefix}-backend-eip"
  bandwidth       = 10
  internet_charge_type = "PayByBandwidth"
}

resource "alicloud_eip_association" "backend" {
  allocation_id = alicloud_eip.backend.id
  instance_id   = alicloud_instance.backend.id
}

# RDS MySQL Instance
resource "alicloud_db_instance" "mysql" {
  engine               = "MySQL"
  engine_version       = "8.0"
  instance_type        = "rds.mysql.s2.large"  # 2 vCPU, 4GB RAM
  instance_storage     = 100  # GB
  vswitch_id           = alicloud_vswitch.main.id
  security_group_id    = alicloud_security_group.rds.id
  instance_charge_type = "Postpaid"
  zone_id              = "${var.alicloud_region}a"

  db_instance_name = "${local.name_prefix}-mysql"

  # Backup settings
  backup_time     = "02:00Z-03:00Z"
  backup_period   = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

  tags = local.common_tags
}

resource "alicloud_db_account" "mysql" {
  db_instance_id = alicloud_db_instance.mysql.id
  account_name   = "paylabs_user"
  password       = var.db_password
  account_type   = "Super"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

# Redis Instance
resource "alicloud_kvstore_instance" "redis" {
  instance_type    = "Redis"
  capacity         = 1  # GB
  instance_charge_type = "Postpaid"
  vswitch_id       = alicloud_vswitch.main.id
  security_ips     = ["10.0.0.0/16"]  # Allow from VPC only

  instance_name = "${local.name_prefix}-redis"

  tags = local.common_tags
}

# Outputs
output "ecs_public_ip" {
  description = "Public IP of the ECS instance"
  value       = alicloud_eip.backend.ip_address
}

output "rds_connection_string" {
  description = "RDS MySQL connection string"
  value       = alicloud_db_instance.mysql.connection_string
}

output "redis_connection_string" {
  description = "Redis connection string"
  value       = alicloud_kvstore_instance.redis.connection_string
}

output "backend_api_url" {
  description = "Backend API URL"
  value       = "http://${alicloud_eip.backend.ip_address}:8000"
}
