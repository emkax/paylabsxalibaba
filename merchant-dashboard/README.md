# PayLabs Merchant Health Intelligence - Frontend

Next.js 16 frontend dashboard for the PayLabs Merchant Health Intelligence Platform.

## Quick Start

### Prerequisites
- Node.js 20+
- npm or bun

### Development

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.local.example .env.local

# Start development server
npm run dev
```

Access the dashboard at: http://localhost:3000

## Environment Variables

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Available Scripts

```bash
npm run dev      # Start development server (http://localhost:3000)
npm run build    # Build for production
npm run start    # Start production server
npm run lint     # Run ESLint
```

## Dashboard Pages

| Page | Route | Description |
|------|-------|-------------|
| **Overview** | `/dashboard/overview` | Health score, KPIs, risk level |
| **Revenue** | `/dashboard/revenue` | Revenue trends, forecasts, anomalies |
| **Cashflow** | `/dashboard/cashflow` | Cash inflow/outflow, liquidity runway |
| **Peer** | `/dashboard/peer` | Peer benchmarking, radar charts |
| **Recommendation** | `/dashboard/recommendation` | AI-generated action items |
| **Simulation** | `/dashboard/simulation` | What-if scenario modeling |

## Key Components

### API Client (`src/lib/api-client.ts`)
Type-safe API client for communicating with the FastAPI backend.

```typescript
import { merchantApi } from '@/lib/api-client';

// Get merchant overview
const overview = await merchantApi.getOverview('MERCHANT001');
```

### React Query Hooks (`src/hooks/useMerchantData.ts`)
Pre-configured hooks with caching and error handling.

```typescript
import { useMerchantOverview } from '@/hooks/useMerchantData';

function Dashboard() {
  const { data, isLoading, error } = useMerchantOverview('MERCHANT001');

  if (isLoading) return <LoadingSkeleton />;
  if (error) return <Error message={error.message} />;

  return <HealthScore score={data.data.healthScore} />;
}
```

### Providers (`src/components/providers.tsx`)
TanStack Query provider with optimized configuration.

```typescript
import { QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000, // 1 minute
      retry: 2,
    },
  },
});
```

## Styling

This project uses **CSS Modules** (not Tailwind CSS) for styling.

```css
/* page.module.css */
.container {
  padding: 24px;
  background: #fff;
  border-radius: 8px;
}

.metric {
  font-size: 24px;
  font-weight: 600;
  color: #1a1a1a;
}
```

```typescript
// page.tsx
import styles from './page.module.css';

export default function Page() {
  return (
    <div className={styles.container}>
      <span className={styles.metric}>75</span>
    </div>
  );
}
```

## Data Flow

```
User Action
    ↓
React Component
    ↓
React Query Hook (useMerchantData.ts)
    ↓
API Client (api-client.ts)
    ↓
FastAPI Backend (http://localhost:8000)
    ↓
Database (MySQL) / AI Services (Qwen)
```

## Chart Components

We use **Recharts** for data visualization.

```typescript
import { LineChart, Line, XAxis, YAxis, Tooltip } from 'recharts';

<LineChart width={600} height={300} data={dailyRevenue}>
  <XAxis dataKey="date" />
  <YAxis />
  <Tooltip />
  <Line type="monotone" dataKey="revenue" stroke="#8884d8" />
</LineChart>
```

## Icons

We use **Lucide React** for icons.

```typescript
import { TrendingUp, TrendingDown, AlertCircle } from 'lucide-react';

<TrendingUp className="text-green-500" />
```

## Type Safety

All data types are defined in `src/lib/api-client.ts`:

```typescript
export interface OverviewData {
  healthScore: number;
  survivalProbability: number;
  riskLevel: 'low' | 'medium' | 'high';
  kpis: {
    revenue: number;
    revenueChange: number;
    volatilityScore: number;
    cashflowStressIndex: number;
    peerPercentile: number;
    repeatRatio: number;
  };
}
```

## Error Handling

```typescript
try {
  const { data } = await merchantApi.getOverview(merchantId);
} catch (error) {
  if (error instanceof ApiError) {
    console.error(`API Error ${error.status}: ${error.message}`);
  }
}
```

## Deployment

### Docker

```bash
# Build and run
docker build -t merchant-dashboard .
docker run -p 3000:3000 merchant-dashboard
```

### Production Build

```bash
npm run build
npm run start
```

### Environment-Specific Builds

```bash
# Production
NEXT_PUBLIC_API_URL=https://api.paylabs.co.id npm run build

# Staging
NEXT_PUBLIC_API_URL=https://api-staging.paylabs.co.id npm run build
```

## Performance Optimization

1. **React Query Caching**: 60s stale time, no refetch on window focus
2. **Code Splitting**: Next.js automatic code splitting
3. **Image Optimization**: Next.js Image component
4. **SSR/SSG**: Mixed strategy based on page requirements

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

Proprietary - PayLabs x Alibaba Cloud Hackathon 2026
