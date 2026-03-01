/**
 * API Client for PayLabs Merchant Health Intelligence Platform
 *
 * This client connects to the FastAPI backend instead of using mock data.
 * Configure NEXT_PUBLIC_API_URL in .env.local to point to your backend.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Types
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
  liquidityRunway: number;
  runwayTarget: number;
}

export interface PeerData {
  percentile: number;
  radarData: { metric: string; merchant: number; peers: number }[];
  comparisonTable: { metric: string; merchant: number; peers: number; industry: number }[];
  peerSegment: 'city' | 'revenue' | 'category';
}

export interface RecommendationData {
  rootCauses: { title: string; description: string; severity: 'high' | 'medium' | 'low' }[];
  immediateActions: ActionItem[];
  strategicActions: ActionItem[];
  expectedImpact: { revenue: number; healthScore: number };
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

export interface Transaction {
  transaction_id: string;
  amount: number;
  currency: string;
  payment_method: string;
  status: string;
  transaction_time: string;
  is_anomaly?: boolean;
  anomaly_score?: number;
}

// API Response wrapper
interface ApiResponse<T> {
  data: T;
  lastUpdated?: string;
  source?: string;
}

// Error handling
class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Unknown error' }));
    throw new ApiError(response.status, error.detail || error.error || 'Request failed');
  }

  return response.json();
}

// Merchant API endpoints
export const merchantApi = {
  /**
   * Get merchant overview data (health score, KPIs)
   */
  async getOverview(merchantId: string, days: number = 30): Promise<ApiResponse<OverviewData>> {
    return fetchApi<ApiResponse<OverviewData>>(
      `/api/merchant/${merchantId}?type=overview&days=${days}`
    );
  },

  /**
   * Get revenue and performance data
   */
  async getPerformance(merchantId: string, days: number = 30): Promise<ApiResponse<RevenueData>> {
    return fetchApi<ApiResponse<RevenueData>>(
      `/api/merchant/${merchantId}?type=performance&days=${days}`
    );
  },

  /**
   * Get cashflow data
   */
  async getCashflow(merchantId: string): Promise<ApiResponse<CashflowData>> {
    return fetchApi<ApiResponse<CashflowData>>(
      `/api/merchant/${merchantId}?type=cashflow`
    );
  },

  /**
   * Get peer benchmark data
   */
  async getPeer(merchantId: string): Promise<ApiResponse<PeerData>> {
    return fetchApi<ApiResponse<PeerData>>(
      `/api/merchant/${merchantId}?type=peer`
    );
  },

  /**
   * Get risk assessment
   */
  async getRisk(merchantId: string, days: number = 30): Promise<ApiResponse<{
    riskLevel: 'low' | 'medium' | 'high';
    riskScore: number;
    factors: { name: string; score: number }[];
  }>> {
    return fetchApi<ApiResponse<{
      riskLevel: 'low' | 'medium' | 'high';
      riskScore: number;
      factors: { name: string; score: number }[];
    }>>(
      `/api/merchant/${merchantId}?type=risk&days=${days}`
    );
  },

  /**
   * Get AI recommendations
   */
  async getRecommendation(merchantId: string, days: number = 30): Promise<ApiResponse<RecommendationData>> {
    return fetchApi<ApiResponse<RecommendationData>>(
      `/api/merchant/${merchantId}?type=recommendation&days=${days}`
    );
  },

  /**
   * Get transactions
   */
  async getTransactions(
    merchantId: string,
    startDate: string,
    endDate: string,
    limit: number = 100,
    offset: number = 0
  ): Promise<{
    data: Transaction[];
    total: number;
    limit: number;
    offset: number;
  }> {
    const params = new URLSearchParams({
      start_date: startDate,
      end_date: endDate,
      limit: limit.toString(),
      offset: offset.toString(),
    });
    return fetchApi(`/api/merchant/${merchantId}/transactions?${params}`);
  },

  /**
   * Run what-if simulation
   */
  async simulate(
    merchantId: string,
    input: SimulationInput
  ): Promise<ApiResponse<SimulationOutput>> {
    const params = new URLSearchParams({
      discount_percentage: input.discountPercentage.toString(),
      cost_reduction: input.costReduction.toString(),
      marketing_boost: input.marketingBoost.toString(),
      delivery_integration: input.deliveryIntegration.toString(),
    });
    return fetchApi<ApiResponse<SimulationOutput>>(
      `/api/merchant/${merchantId}/simulate?${params}`,
      { method: 'POST' }
    );
  },
};

// AI API endpoints
export const aiApi = {
  /**
   * Get AI-generated insights
   */
  async getInsights(merchantId: string, days: number = 30): Promise<{
    data: RecommendationData;
    merchantId: string;
    analysisDate: string;
  }> {
    return fetchApi(`/api/ai/${merchantId}/insights?days=${days}`);
  },

  /**
   * Detect transaction anomalies
   */
  async detectAnomalies(merchantId: string, days: number = 30): Promise<{
    data: {
      transactions: (Transaction & { is_anomaly: boolean; anomaly_score: number })[];
      totalAnomalies: number;
      anomalyRate: number;
    };
    analyzedAt: string;
  }> {
    return fetchApi(`/api/ai/${merchantId}/anomalies?days=${days}`);
  },

  /**
   * Get revenue forecast
   */
  async getForecast(merchantId: string, periods: number = 7): Promise<{
    data: {
      historical: { date: string; revenue: number }[];
      forecast: { date: string; forecast: number }[];
    };
    forecastedAt: string;
  }> {
    return fetchApi(`/api/ai/${merchantId}/forecast?periods=${periods}`);
  },

  /**
   * Analyze a single transaction for anomalies
   */
  async analyzeTransaction(
    merchantId: string,
    transactionId: string
  ): Promise<{
    data: {
      transaction_id: string;
      amount: number;
      is_anomaly: boolean;
      anomaly_score: number;
      reasons: string[];
    };
    analyzedAt: string;
  }> {
    return fetchApi(`/api/ai/analyze-transaction?merchant_id=${merchantId}&transaction_id=${transactionId}`, {
      method: 'POST',
    });
  },

  /**
   * Get stored recommendations
   */
  async getRecommendations(
    merchantId: string,
    status: string = 'pending',
    limit: number = 10
  ): Promise<{
    data: Array<{
      id: number;
      type: string;
      title: string;
      description: string;
      severity: string;
      priority: string;
      status: string;
      expected_revenue_impact: number;
      expected_health_impact: number;
      created_at: string;
    }>;
    total: number;
  }> {
    return fetchApi(`/api/ai/recommendations/${merchantId}?status=${status}&limit=${limit}`);
  },

  /**
   * Mark recommendation as implemented
   */
  async markImplemented(recommendationId: number): Promise<{
    success: boolean;
    data: {
      id: number;
      status: string;
      implemented_at: string;
    };
  }> {
    return fetchApi(`/api/ai/recommendations/${recommendationId}/implement`, {
      method: 'POST',
    });
  },
};

// Health check
export async function checkApiHealth(): Promise<{
  status: string;
  database?: string;
  timestamp: string;
}> {
  return fetchApi('/health');
}

// Export for use in hooks
export default {
  merchant: merchantApi,
  ai: aiApi,
  checkHealth: checkApiHealth,
};
