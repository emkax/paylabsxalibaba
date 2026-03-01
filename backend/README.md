# PayLabs Merchant Health Intelligence - Backend

FastAPI backend for the PayLabs Merchant Health Intelligence Platform.

## Quick Start

### Prerequisites
- Python 3.11+
- MySQL 8.0+
- Redis 7+
- Docker (optional, for containerized deployment)

### Local Development

1. **Install dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Initialize database:**
```bash
# MySQL should be running with the database created
# Tables are auto-created on first run
```

4. **Run the server:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

5. **Access API docs:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Docker Development

```bash
# From project root
docker-compose up -d backend mysql redis
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | MySQL connection string | `mysql+pymysql://root:password@localhost:3306/paylabs_merchant` |
| `REDIS_HOST` | Redis host | `localhost` |
| `REDIS_PORT` | Redis port | `6379` |
| `DASHSCOPE_API_KEY` | Alibaba Cloud Qwen API key | - |
| `PAYLABS_MERCHANT_ID` | PayLabs merchant ID | `010614` |
| `PAYLABS_PRIVATE_KEY_PATH` | Path to private key | `private_key.pem` |
| `PAYLABS_API_URL` | PayLabs API URL | `https://api-sit.paylabs.co.id` |

## API Endpoints

### Merchant Endpoints

```
GET  /api/merchant/{id}?type=overview         - Health score & KPIs
GET  /api/merchant/{id}?type=performance      - Revenue & transactions
GET  /api/merchant/{id}?type=cashflow         - Cash flow analysis
GET  /api/merchant/{id}?type=peer             - Peer benchmarking
GET  /api/merchant/{id}?type=recommendation   - AI recommendations
GET  /api/merchant/{id}?type=risk             - Risk assessment
POST /api/merchant/{id}/simulate              - What-if simulation
GET  /api/merchant/{id}/transactions          - Transaction history
```

### AI Endpoints

```
GET  /api/ai/{id}/insights                    - AI-generated insights
GET  /api/ai/{id}/anomalies                   - Anomaly detection
GET  /api/ai/{id}/forecast                    - Revenue forecast
POST /api/ai/analyze-transaction              - Single transaction analysis
GET  /api/ai/recommendations/{id}             - Stored recommendations
POST /api/ai/recommendations/{id}/implement   - Mark as implemented
```

## Project Structure

```
backend/
├── api/
│   └── routes/
│       ├── merchant.py    # Merchant endpoints
│       └── ai.py          # AI endpoints
├── models/
│   └── transaction.py     # SQLAlchemy models
├── services/
│   ├── paylabs_client.py  # PayLabs API client
│   ├── ai_service.py      # Qwen AI integration
│   └── analytics_service.py # Analytics & ML
├── database/
│   └── init.sql          # Database initialization
├── database.py            # DB connection
├── main.py                # FastAPI app
├── requirements.txt       # Dependencies
└── Dockerfile
```

## Key Services

### PayLabs Client
Handles authentication and communication with PayLabs Payment Gateway API.
- Signature generation for request authentication
- Transaction ingestion
- Merchant info retrieval

### AI Service (Qwen)
Integrates with Alibaba Cloud Qwen API for natural language insights.
- Merchant health analysis
- Recommendation generation
- Anomaly explanation

### Analytics Service
Calculates health scores and detects anomalies.
- Health score calculation (weighted components)
- Isolation Forest for anomaly detection
- Revenue forecasting (time-series)
- Peer benchmarking

## Testing

```bash
# Run tests (when implemented)
pytest

# Test specific endpoint
curl http://localhost:8000/api/merchant/MERCHANT001?type=overview
```

## Deployment

### Alibaba Cloud ECS

1. **Build and push Docker image:**
```bash
docker build -t registry.ap-southeast-1.aliyuncs.com/paylabs/merchant-health:latest .
docker push registry.ap-southeast-1.aliyuncs.com/paylabs/merchant-health:latest
```

2. **Deploy to ECS:**
```bash
# SSH into ECS
ssh root@<ecs-public-ip>

# Pull and run
docker pull registry.ap-southeast-1.aliyuncs.com/paylabs/merchant-health:latest
docker run -d -p 8000:8000 --env-file .env merchant-health:latest
```

### Terraform Deployment

```bash
cd infrastructure/terraform
terraform init
terraform apply
```

## Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Logs
```bash
# Docker logs
docker logs <container-id>

# Uvicorn logs
# View in terminal where server is running
```

## Troubleshooting

### Database Connection Error
- Verify MySQL is running: `docker ps | grep mysql`
- Check connection string in `.env`
- Ensure database exists: `mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS paylabs_merchant;"`

### Redis Connection Error
- Verify Redis is running: `docker ps | grep redis`
- Test connection: `redis-cli ping`

### Qwen API Error
- Verify API key in `.env`
- Check API quota: https://dashscope.console.aliyun.com/
- Fallback to rule-based insights if API unavailable

## License

Proprietary - PayLabs x Alibaba Cloud Hackathon 2026
