# PayLabs Merchant Health Intelligence Platform - Architecture

## System Overview

```
┌─────────────────┐     ┌──────────────────────────┐     ┌─────────────────┐
│  PayLabs API    │────▶│   Backend (FastAPI)      │────▶│  Next.js Dashboard │
│  (Payment GW)   │     │   - ECS Instance         │     │  - Frontend UI    │
└─────────────────┘     │   - RDS MySQL (data)     │     └─────────────────┘
                        │   - Redis (cache)        │
                        │                          │
                        │   ┌──────────────────┐   │
                        │   │  Alibaba AI      │   │
                        │   │  - Qwen API      │   │
                        │   │  - PAI (ML)      │   │
                        │   └──────────────────┘   │
                        └──────────────────────────┘
```

## Technology Stack

### Frontend
- **Framework:** Next.js 16 (App Router)
- **Language:** TypeScript
- **State Management:** TanStack Query (React Query)
- **Charts:** Recharts
- **Styling:** CSS Modules (native)
- **Icons:** Lucide React

### Backend
- **Framework:** FastAPI (Python 3.11)
- **Database ORM:** SQLAlchemy
- **API Server:** Uvicorn
- **Validation:** Pydantic

### Database & Cache
- **Primary Database:** MySQL 8.0 (Alibaba Cloud RDS)
- **Cache:** Redis 7 (Alibaba Cloud KVStore)

### AI Services
- **LLM:** Alibaba Cloud Qwen (Tongyi Qianwen)
- **ML Platform:** Alibaba Cloud PAI (Platform of AI)
- **Analytics:** scikit-learn, pandas, numpy

### Infrastructure
- **Cloud Provider:** Alibaba Cloud
- **Compute:** ECS (Elastic Compute Service)
- **Container:** Docker, docker-compose
- **IaC:** Terraform

## Project Structure

```
paylabsxalibaba/
├── backend/                    # FastAPI backend
│   ├── api/
│   │   └── routes/            # API route handlers
│   │       ├── merchant.py    # Merchant endpoints
│   │       └── ai.py          # AI endpoints
│   ├── models/                # SQLAlchemy models
│   │   └── transaction.py
│   ├── services/              # Business logic
│   │   ├── paylabs_client.py  # PayLabs API client
│   │   ├── ai_service.py      # Qwen AI integration
│   │   └── analytics_service.py # Analytics & ML
│   ├── database.py            # DB connection
│   ├── main.py                # FastAPI app
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile
├── merchant-dashboard/        # Next.js frontend
│   ├── src/
│   │   ├── app/              # Next.js App Router
│   │   ├── components/       # React components
│   │   ├── hooks/            # React Query hooks
│   │   └── lib/              # Utilities & API client
│   ├── package.json
│   └── Dockerfile
├── infrastructure/
│   └── terraform/            # Alibaba Cloud IaC
│       └── main.tf
├── create/                   # PayLabs signature utils (existing)
├── query/                    # PayLabs query utils (existing)
├── qwen_analysis/            # Qwen AI analysis (existing)
├── docker-compose.yml        # Local development
└── CLAUDE.md                 # Development guide
```

## API Endpoints

### Merchant Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/merchant/{id}?type=overview` | Health score & KPIs |
| GET | `/api/merchant/{id}?type=performance` | Revenue & transactions |
| GET | `/api/merchant/{id}?type=cashflow` | Cash flow analysis |
| GET | `/api/merchant/{id}?type=peer` | Peer benchmarking |
| GET | `/api/merchant/{id}?type=risk` | Risk assessment |
| GET | `/api/merchant/{id}?type=recommendation` | AI recommendations |
| POST | `/api/merchant/{id}/simulate` | What-if simulation |
| GET | `/api/merchant/{id}/transactions` | Transaction history |

### AI Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/ai/{id}/insights` | AI-generated insights |
| GET | `/api/ai/{id}/anomalies` | Anomaly detection |
| GET | `/api/ai/{id}/forecast` | Revenue forecast |
| POST | `/api/ai/analyze-transaction` | Single transaction analysis |
| GET | `/api/ai/recommendations/{id}` | Stored recommendations |
| POST | `/api/ai/recommendations/{id}/implement` | Mark as implemented |

## Database Schema

### Tables

1. **transactions** - Payment transaction records
   - `transaction_id`, `merchant_id`, `amount`, `status`, `payment_method`
   - `is_anomaly`, `anomaly_score`, `transaction_time`

2. **merchant_health_snapshots** - Daily health metrics
   - `health_score`, `survival_probability`, `risk_level`
   - `volatility_score`, `cashflow_stress_index`, `peer_percentile`

3. **ai_recommendations** - AI-generated recommendations
   - `recommendation_type`, `title`, `description`, `severity`
   - `expected_revenue_impact`, `expected_health_impact`

4. **simulation_results** - What-if simulation history
   - `discount_percentage`, `cost_reduction`, `marketing_boost`
   - `forecasted_revenue`, `updated_health_score`

## Key Features

### 1. Health Score Calculation
- Revenue health (25% weight)
- Stability health (25% weight)
- Cashflow health (25% weight)
- Peer performance (15% weight)
- Customer retention (10% weight)

### 2. AI Recommendations (Qwen)
- Natural language insights
- Root cause analysis
- Immediate actions (1-week implementation)
- Strategic actions (long-term)
- Expected impact estimation

### 3. Anomaly Detection (Isolation Forest)
- Transaction amount anomalies
- Time-based pattern detection
- Z-score analysis for small datasets
- Confidence scoring

### 4. Revenue Forecasting
- Weighted moving average
- Trend detection
- 7-day forward projection
- Historical comparison

### 5. What-If Simulation
- Discount impact modeling
- Cost reduction scenarios
- Marketing boost projections
- Delivery integration effects

## Deployment

### Local Development
```bash
# Start all services
docker-compose up -d

# Backend only
cd backend && uvicorn main:app --reload

# Frontend only
cd merchant-dashboard && npm run dev
```

### Alibaba Cloud Deployment
```bash
# Initialize Terraform
cd infrastructure/terraform
terraform init

# Plan and apply
terraform plan
terraform apply

# Deploy backend to ECS
# (SSH into ECS and run docker-compose)
```

## Environment Variables

### Backend (.env)
```
DATABASE_URL=mysql+pymysql://user:pass@host:3306/paylabs_merchant
REDIS_HOST=localhost
REDIS_PORT=6379
DASHSCOPE_API_KEY=your_api_key
PAYLABS_MERCHANT_ID=010614
PAYLABS_PRIVATE_KEY_PATH=private_key.pem
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Security Considerations

1. **API Authentication**: PayLabs signature-based auth
2. **Database**: Private network access only
3. **CORS**: Restricted to frontend domain
4. **Environment Variables**: Never commit sensitive data
5. **Rate Limiting**: Implement for production

## Performance Optimization

1. **Redis Caching**: 5-minute cache for frequently accessed data
2. **Database Indexing**: Optimized for common queries
3. **Lazy Loading**: Pagination for transaction lists
4. **CDN**: Static assets via Alibaba Cloud CDN

## Monitoring & Logging

- **Application Logs**: Structured JSON logging
- **API Metrics**: Request latency, error rates
- **Database**: Slow query log, connection pool metrics
- **AI API**: Token usage, response times

## Future Enhancements

1. **Real-time Updates**: WebSocket for live transactions
2. **Advanced ML**: Deep learning for forecasting
3. **Multi-merchant**: Aggregated portfolio view
4. **Mobile App**: React Native companion app
5. **Export Features**: PDF reports, CSV exports
