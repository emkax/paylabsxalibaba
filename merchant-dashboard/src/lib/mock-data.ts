// Mock data generators for the Merchant Health Dashboard

import { addDays, subDays, format } from 'date-fns';

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
  lastUpdated: string;
}

export interface RevenueData {
  dailyRevenue: { date: string; revenue: number; forecast?: number; isAnomaly?: boolean }[];
  transactionFrequency: { date: string; count: number }[];
  totalTransactions: number;
  averageTransactionValue: number;
}

export interface CashflowData {
  inflow: { date: string; amount: number }[];
  outflow: { date: string; amount: number }[];
  netCashflow: { date: string; amount: number }[];
  negativeStreak: number;
  liquidityRunway: number; // in days
  runwayTarget: number;
}

export interface PeerData {
  percentile: number;
  radarData: {
    metric: string;
    merchant: number;
    peers: number;
  }[];
  comparisonTable: {
    metric: string;
    merchant: number;
    peers: number;
    industry: number;
  }[];
  peerSegment: 'city' | 'revenue' | 'category';
}

export interface RecommendationData {
  rootCauses: { title: string; description: string; severity: 'high' | 'medium' | 'low' }[];
  immediateActions: ActionItem[];
  strategicActions: ActionItem[];
  expectedImpact: {
    revenue: number;
    healthScore: number;
  };
}

export interface ActionItem {
  id: string;
  title: string;
  description: string;
  expectedImpact: string;
  status: 'pending' | 'implemented';
  priority: 'high' | 'medium' | 'low';
}

export interface SimulationInput {
  discountPercentage: number;
  costReduction: number;
  marketingBoost: number;
  deliveryIntegration: boolean;
}

export interface SimulationOutput {
  forecastedRevenue: number;
  updatedHealthScore: number;
  updatedSurvivalProbability: number;
  impact: {
    revenue: number;
    healthScore: number;
    survivalProbability: number;
  };
}

// Generate mock overview data
export function generateOverviewData(merchantId: string): OverviewData {
  const healthScore = Math.floor(Math.random() * 30) + 65; // 65-95
  const survivalProbability = Math.floor(Math.random() * 25) + 70; // 70-95%

  let riskLevel: 'low' | 'medium' | 'high' = 'low';
  if (healthScore < 70) riskLevel = 'high';
  else if (healthScore < 80) riskLevel = 'medium';

  return {
    healthScore,
    survivalProbability,
    riskLevel,
    kpis: {
      revenue: Math.floor(Math.random() * 500000000) + 100000000, // 100M - 600M
      revenueChange: parseFloat((Math.random() * 20 - 5).toFixed(2)), // -5% to +15%
      volatilityScore: Math.floor(Math.random() * 40) + 10, // 10-50
      cashflowStressIndex: Math.floor(Math.random() * 60) + 10, // 10-70
      peerPercentile: Math.floor(Math.random() * 40) + 50, // 50-90
      repeatRatio: parseFloat((Math.random() * 0.4 + 0.4).toFixed(2)), // 0.4-0.8
    },
    lastUpdated: new Date().toISOString(),
  };
}

// Generate mock revenue data
export function generateRevenueData(days: number = 30): RevenueData {
  const dailyRevenue: { date: string; revenue: number; forecast?: number; isAnomaly?: boolean }[] = [];
  const transactionFrequency: { date: string; count: number }[] = [];

  let totalRevenue = 0;
  let totalTransactions = 0;
  const baseRevenue = Math.random() * 5000000 + 2000000; // 2M - 7M base
  const baseTransactions = Math.floor(Math.random() * 500) + 200;

  for (let i = days - 1; i >= 0; i--) {
    const date = format(subDays(new Date(), i), 'yyyy-MM-dd');

    // Add some seasonality (weekends lower)
    const dayOfWeek = new Date().getDay();
    const weekendFactor = (dayOfWeek === 0 || dayOfWeek === 6) ? 0.7 : 1;

    const variance = (Math.random() * 0.4 - 0.2); // +/- 20%
    const revenue = Math.floor(baseRevenue * weekendFactor * (1 + variance));
    const transactions = Math.floor(baseTransactions * weekendFactor * (1 + variance * 0.5));

    // Add anomaly for 1-2 days
    const isAnomaly = Math.random() < 0.05;
    if (isAnomaly) {
      dailyRevenue.push({
        date,
        revenue: Math.floor(revenue * 0.3), // 70% drop
        isAnomaly: true,
      });
    } else {
      dailyRevenue.push({ date, revenue });
    }

    transactionFrequency.push({ date, count: transactions });

    totalRevenue += revenue;
    totalTransactions += transactions;
  }

  // Add forecast for next 7 days
  const lastRevenue = dailyRevenue[dailyRevenue.length - 1].revenue;
  for (let i = 1; i <= 7; i++) {
    const date = format(addDays(new Date(), i), 'yyyy-MM-dd');
    const forecast = Math.floor(lastRevenue * (1 + (Math.random() * 0.1 - 0.05)));
    dailyRevenue.push({ date, revenue: 0, forecast });
  }

  return {
    dailyRevenue,
    transactionFrequency,
    totalTransactions,
    averageTransactionValue: Math.floor(totalRevenue / totalTransactions),
  };
}

// Generate mock cashflow data
export function generateCashflowData(): CashflowData {
  const days = 30;
  const inflow: { date: string; amount: number }[] = [];
  const outflow: { date: string; amount: number }[] = [];
  const netCashflow: { date: string; amount: number }[] = [];

  let negativeStreak = 0;
  const baseInflow = Math.random() * 5000000 + 3000000;
  const baseOutflow = baseInflow * (0.7 + Math.random() * 0.4); // 70-110% of inflow

  for (let i = days - 1; i >= 0; i--) {
    const date = format(subDays(new Date(), i), 'yyyy-MM-dd');
    const inflowAmount = Math.floor(baseInflow * (0.8 + Math.random() * 0.4));
    const outflowAmount = Math.floor(baseOutflow * (0.8 + Math.random() * 0.4));
    const net = inflowAmount - outflowAmount;

    inflow.push({ date, amount: inflowAmount });
    outflow.push({ date, amount: outflowAmount });
    netCashflow.push({ date, amount: net });

    if (net < 0) {
      negativeStreak++;
    } else {
      negativeStreak = 0;
    }
  }

  // Calculate liquidity runway (simplified)
  const avgBurn = Math.floor(outflow.reduce((a, b) => a + b.amount, 0) / days);
  const cashReserves = Math.floor(Math.random() * 100000000) + 50000000; // 50M - 150M
  const liquidityRunway = Math.floor(cashReserves / avgBurn);

  return {
    inflow,
    outflow,
    netCashflow,
    negativeStreak: Math.min(negativeStreak, 5), // Cap at 5 for display
    liquidityRunway,
    runwayTarget: 90, // 90 days target
  };
}

// Generate mock peer benchmark data
export function generatePeerData(): PeerData {
  const percentile = Math.floor(Math.random() * 40) + 50; // 50-90

  return {
    percentile,
    radarData: [
      { metric: 'Revenue Growth', merchant: Math.random() * 80 + 20, peers: Math.random() * 60 + 30 },
      { metric: 'Cash Flow', merchant: Math.random() * 70 + 30, peers: Math.random() * 50 + 40 },
      { metric: 'Customer Retention', merchant: Math.random() * 90 + 10, peers: Math.random() * 60 + 30 },
      { metric: 'Transaction Volume', merchant: Math.random() * 80 + 20, peers: Math.random() * 60 + 30 },
      { metric: 'Avg Order Value', merchant: Math.random() * 70 + 30, peers: Math.random() * 50 + 40 },
      { metric: 'Profit Margin', merchant: Math.random() * 60 + 30, peers: Math.random() * 50 + 30 },
    ],
    comparisonTable: [
      { metric: 'Monthly Revenue', merchant: 156000000, peers: 125000000, industry: 98000000 },
      { metric: 'Growth Rate (%)', merchant: 12.5, peers: 8.3, industry: 5.2 },
      { metric: 'Customer Retention (%)', merchant: 78, peers: 65, industry: 58 },
      { metric: 'Avg Transaction (IDR)', merchant: 485000, peers: 420000, industry: 380000 },
      { metric: 'Monthly Transactions', merchant: 321, peers: 298, industry: 257 },
    ],
    peerSegment: 'city',
  };
}

// Generate mock recommendations
export function generateRecommendationData(): RecommendationData {
  return {
    rootCauses: [
      {
        title: 'Revenue Volatility',
        description: 'High day-to-day revenue fluctuations indicate inconsistent customer demand or payment issues.',
        severity: 'high',
      },
      {
        title: 'Cash Flow Pressure',
        description: 'Recent negative cash flow streak is reducing your liquidity runway.',
        severity: 'medium',
      },
      {
        title: 'Below-Average Peer Performance',
        description: 'Your growth rate is trailing similar merchants in your city.',
        severity: 'medium',
      },
    ],
    immediateActions: [
      {
        id: '1',
        title: 'Implement Weekend Promotions',
        description: 'Launch targeted weekend discounts to boost low-period sales.',
        expectedImpact: '+15% weekend revenue',
        status: 'pending',
        priority: 'high',
      },
      {
        id: '2',
        title: 'Review Payment Gateway Success Rate',
        description: 'Analyze failed transactions and optimize payment flow.',
        expectedImpact: '-20% payment failures',
        status: 'pending',
        priority: 'high',
      },
      {
        id: '3',
        title: 'Negotiate Supplier Terms',
        description: 'Extend payment terms with key suppliers to improve cash flow.',
        expectedImpact: '+10 days liquidity runway',
        status: 'pending',
        priority: 'medium',
      },
    ],
    strategicActions: [
      {
        id: '4',
        title: 'Expand Product Categories',
        description: 'Add complementary products to increase average order value.',
        expectedImpact: '+25% AOV',
        status: 'pending',
        priority: 'medium',
      },
      {
        id: '5',
        title: 'Implement Loyalty Program',
        description: 'Launch rewards program to increase customer retention.',
        expectedImpact: '+20% repeat purchases',
        status: 'pending',
        priority: 'medium',
      },
      {
        id: '6',
        title: 'Integrate Delivery Platforms',
        description: 'Connect with GoFood, GrabFood for expanded reach.',
        expectedImpact: '+30% order volume',
        status: 'pending',
        priority: 'low',
      },
    ],
    expectedImpact: {
      revenue: 23, // 23% increase
      healthScore: 12, // 12 point increase
    },
  };
}

// Generate mock simulation output
export function generateSimulationOutput(input: SimulationInput): SimulationOutput {
  const baseHealthScore = 75;
  const baseSurvivalProbability = 82;
  const baseRevenue = 156000000;

  // Calculate impact based on inputs
  const discountImpact = input.discountPercentage * 0.8; // Each % discount = 0.8% revenue boost
  const costReductionImpact = input.costReduction * 1.2; // Each % cost reduction = 1.2% health boost
  const marketingImpact = input.marketingBoost * 0.6; // Each % marketing = 0.6% revenue boost
  const deliveryImpact = input.deliveryIntegration ? 15 : 0; // 15% boost from delivery integration

  const revenueImpact = discountImpact + marketingImpact + deliveryImpact;
  const healthImpact = costReductionImpact + (revenueImpact * 0.3);
  const survivalImpact = healthImpact * 0.8;

  return {
    forecastedRevenue: Math.floor(baseRevenue * (1 + revenueImpact / 100)),
    updatedHealthScore: Math.min(100, Math.floor(baseHealthScore + healthImpact)),
    updatedSurvivalProbability: Math.min(100, Math.floor(baseSurvivalProbability + survivalImpact)),
    impact: {
      revenue: parseFloat(revenueImpact.toFixed(1)),
      healthScore: parseFloat(healthImpact.toFixed(1)),
      survivalProbability: parseFloat(survivalImpact.toFixed(1)),
    },
  };
}
