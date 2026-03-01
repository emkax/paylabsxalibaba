# Merchant Health & Survival Intelligence Dashboard

## 1. Technology Stack

Framework: Next.js (React 18+)
Language: TypeScript
State Management: React Query (TanStack Query)
Routing: Next.js App Router
Styling: Native CSS Modules (No Tailwind)
Charts: Recharts / ECharts
Deployment Target: Alibaba Cloud ECS

## 2. Frontend Architecture

- Modular page-based structure (Next.js app directory)
- API communication via React Query
- SSR for overview pages (optional)
- CSR for dynamic simulation panel
- Code splitting per route

## 3. Core Dashboard Pages

/dashboard
/dashboard/overview
/dashboard/revenue
/dashboard/cashflow
/dashboard/peer
/dashboard/recommendation
/dashboard/simulation

## 4. Overview Module Requirements

- Health Score Gauge (0–100)
- Survival Probability Display
- Risk Level Badge
- KPI Cards:


Revenue, Revenue Change %, Volatility Score,
Cashflow Stress Index, Peer Percentile, Repeat Ratio

- Interactive hover tooltips

## 5. Revenue Analytics Module

- Revenue Line Chart (30D / 60D / 90D toggle)
- Forecast projection line
- Anomaly highlighting
- Transaction frequency bar chart
- CSV export button
- Date range picker

## 6. Cashflow Monitoring Module

- Inflow vs Outflow chart
- Net cashflow visualization
- Negative streak indicator
- Liquidity runway progress bar
- Scenario slider (cost reduction %)

## 7. Peer Benchmark Module

- Percentile rank gauge
- Radar comparison chart
- Industry comparison table
- Toggle between peer segmentation (City / Revenue Bracket / Category)

## 8. AI Recommendation Module

- Root Cause Analysis section
- Immediate Actions (30 days)
- Strategic Actions (90 days)
- Expected KPI impact
- Action status toggle (Implemented / Pending)


- Impact simulation trigger

## 9. Simulation Panel

User controls:

- Discount percentage slider
- Cost reduction slider
- Marketing boost slider
- Delivery integration toggle

System recalculates:

- Forecasted revenue
- Updated Health Score
- Updated Survival Probability

## 10. API Integration

GET /merchant/:id/overview
GET /merchant/:id/performance
GET /merchant/:id/peer
GET /merchant/:id/risk
GET /merchant/:id/recommendation
POST /merchant/:id/simulate

All endpoints return JSON + last_updated timestamp.

## 11. Performance Requirements

- First Contentful Paint < 2.5s
- Chart render < 1s
- Lazy load heavy components
- Skeleton loading during data fetch

## 12. Security Requirements


- Role-based UI access
- Token-based authentication
- Encrypted API communication (HTTPS)
- Secure environment variables

## 13. UX Requirements

- Clean fintech design
- Native CSS with modular architecture
- Responsive grid layout
- Dark mode support
- Smooth animation transitions


