# Production Deployment Guide - Alibaba Cloud ECS

This guide covers deploying the PayLabs Merchant Health Intelligence Platform to Alibaba Cloud ECS using Terraform.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Alibaba Cloud (Singapore)                 │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  VPC: 10.0.0.0/16                                    │   │
│  │                                                       │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │  ECS Instance (Ubuntu 22.04)                   │  │   │
│  │  │  - 2 vCPU, 8GB RAM (ecs.g6.large)             │  │   │
│  │  │  - Docker & Docker Compose                     │  │   │
│  │  │  ┌──────────────────────────────────────────┐  │  │   │
│  │  │  │  Docker Containers                       │  │  │   │
│  │  │  │  - Backend (FastAPI) :8000               │  │  │   │
│  │  │  │  - Frontend (Next.js) :3000              │  │  │   │
│  │  │  │  - MySQL :3306                           │  │  │   │
│  │  │  │  - Redis :6379                           │  │  │   │
│  │  │  └──────────────────────────────────────────┘  │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  │                                                       │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │  RDS MySQL 8.0 (Managed)                       │  │   │
│  │  │  - 2 vCPU, 4GB RAM                             │  │   │
│  │  │  - 100GB Storage                               │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  │                                                       │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │  Redis KVStore (Managed)                       │  │   │
│  │  │  - 1GB Capacity                                │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  Public Access via EIP:                                      │
│  - HTTP :8000 (Backend API)                                  │
│  - HTTPS :443 (Frontend - for SSL termination)               │
│  - HTTP :3000 (Frontend - direct)                            │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

1. **Alibaba Cloud Account** with active subscription
2. **Terraform** >= 1.0.0 installed locally
3. **Alibaba Cloud CLI** configured (optional, for verification)
4. **Access Keys** (AccessKey ID and Secret)

## Quick Start

### Step 1: Configure Terraform Variables

Create a `terraform.tfvars` file in `infrastructure/terraform/`:

```bash
cd infrastructure/terraform
cat > terraform.tfvars << EOF
alicloud_access_key = "YOUR_ACCESS_KEY_ID"
alicloud_secret_key = "YOUR_SECRET_KEY"
alicloud_region     = "ap-southeast-1"  # Singapore
environment         = "prod"
db_password         = "YourSecurePassword123!"
EOF
```

> **Security Note**: Never commit `terraform.tfvars` to version control. It's gitignored by default.

### Step 2: Initialize and Plan

```bash
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Review the execution plan
terraform plan
```

### Step 3: Apply Infrastructure

```bash
# Apply the configuration
terraform apply -auto-approve

# Note the outputs - they contain your connection strings
terraform output
```

### Step 4: SSH into ECS Instance

```bash
# Get the public IP
ECS_IP=$(terraform output -raw ecs_public_ip)

# SSH into the instance
ssh root@$ECS_IP
```

### Step 5: Deploy Application on ECS

Once SSH'd into the ECS instance:

```bash
# Clone the repository
git clone https://github.com/emkax/paylabsxalibaba.git
cd paylabsxalibaba

# Create environment file
cat > .env << EOF
DASHSCOPE_API_KEY=your_dashscope_api_key
PAYLABS_MERCHANT_ID=010614
FRONTEND_URL=http://$ECS_IP:3000
NEXT_PUBLIC_API_URL=http://$ECS_IP:8000
EOF

# Start all services with Docker Compose
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

## Ports and Access

| Service | Port | URL |
|---------|------|-----|
| Frontend | 3000 | http://ECS_IP:3000 |
| Backend API | 8000 | http://ECS_IP:8000 |
| API Docs (Swagger) | 8000 | http://ECS_IP:8000/docs |
| MySQL | 3306 | Internal (RDS) |
| Redis | 6379 | Internal (KVStore) |

## Security Groups

The following inbound rules are configured:

| Port | Protocol | Source | Description |
|------|----------|--------|-------------|
| 22 | TCP | 0.0.0.0/0 | SSH Access |
| 3000 | TCP | 0.0.0.0/0 | Frontend (Next.js) |
| 443 | TCP | 0.0.0.0/0 | Frontend HTTPS (for SSL termination) |
| 8000 | TCP | 0.0.0.0/0 | Backend API |

### Recommended: Restrict SSH Access

For production, restrict SSH to your IP:

```bash
# In terraform.tfvars or directly in main.tf
# Change the SSH security group rule CIDR
# From: cidr_ip = "0.0.0.0/0"
# To:   cidr_ip = "YOUR_IP/32"
```

## Environment Variables

### Backend (.env on ECS)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | MySQL connection string (auto-configured) |
| `REDIS_HOST` | Yes | Redis host (auto-configured) |
| `REDIS_PORT` | Yes | Redis port (auto-configured) |
| `DASHSCOPE_API_KEY` | Yes | Alibaba Cloud DashScope API key |
| `PAYLABS_MERCHANT_ID` | No | PayLabs merchant ID (default: 010614) |
| `FRONTEND_URL` | No | Frontend URL for CORS |

### Frontend (.env on ECS)

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | Backend API URL |

## Monitoring

### Check Container Status

```bash
docker-compose ps
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Check Resource Usage

```bash
# Docker stats
docker stats

# System resources
htop
df -h
```

## Cost Estimate

| Resource | Specification | Monthly Cost (USD) |
|----------|---------------|-------------------|
| ECS | ecs.g6.large (2 vCPU, 8GB) | ~$70 |
| RDS | rds.mysql.s2.large (2 vCPU, 4GB, 100GB) | ~$100 |
| Redis | 1GB KVStore | ~$15 |
| EIP | 10 Mbps | ~$20 |
| **Total** | | **~$205/month** |

> Costs are approximate and may vary. Check [Alibaba Cloud Pricing](https://www.alibabacloud.com/pricing) for accurate estimates.

## Troubleshooting

### Backend Not Starting

```bash
# Check logs
docker-compose logs backend

# Verify database connection
docker-compose exec backend python -c "from database import SessionLocal; print(SessionLocal().execute('SELECT 1'))"
```

### Frontend Not Accessible

```bash
# Check if container is running
docker-compose ps frontend

# Check network connectivity
docker-compose exec frontend wget -qO- http://backend:8000/health
```

### Database Connection Issues

```bash
# Check RDS connection string
terraform output rds_connection_string

# Verify security group allows ECS
# RDS should allow 10.0.0.0/16
```

## Cleanup

To destroy all resources:

```bash
cd infrastructure/terraform
terraform destroy -auto-approve
```

## Next Steps

### Recommended Production Enhancements

1. **SSL/TLS Certificate**
   - Use Alibaba Cloud SSL Certificates Service
   - Or use Let's Encrypt with certbot inside container

2. **Server Load Balancer (SLB)**
   - Add SLB for high availability
   - Configure health checks

3. **Auto Scaling**
   - Configure auto-scaling group for ECS
   - Set up scaling policies based on CPU/memory

4. **Monitoring & Alerts**
   - Enable CloudMonitor
   - Configure alerts for CPU, memory, disk
   - Set up Log Service (SLS) for centralized logging

5. **Secrets Management**
   - Migrate to Alibaba Cloud Secrets Manager
   - Remove secrets from environment files

6. **CI/CD Pipeline**
   - Set up GitHub Actions or Jenkins
   - Automate builds and deployments

## Support

For issues:
- GitHub Issues: https://github.com/emkax/paylabsxalibaba/issues
- Architecture documentation: See `ARCHITECTURE.md`
- Project overview: See `README.md`
