/**
 * React Query Hooks for Merchant Data
 *
 * These hooks provide typed access to the PayLabs Merchant Health API
 * with automatic caching, refetching, and error handling.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { merchantApi, aiApi, type SimulationInput } from '@/lib/api-client';

// Query keys
export const merchantQueryKeys = {
  all: ['merchant'] as const,
  overview: (merchantId: string) => ['merchant', merchantId, 'overview'] as const,
  performance: (merchantId: string, days: number) => ['merchant', merchantId, 'performance', days] as const,
  cashflow: (merchantId: string) => ['merchant', merchantId, 'cashflow'] as const,
  peer: (merchantId: string) => ['merchant', merchantId, 'peer'] as const,
  risk: (merchantId: string, days: number) => ['merchant', merchantId, 'risk', days] as const,
  recommendation: (merchantId: string, days: number) => ['merchant', merchantId, 'recommendation', days] as const,
  transactions: (merchantId: string, startDate: string, endDate: string) =>
    ['merchant', merchantId, 'transactions', startDate, endDate] as const,
  simulation: (merchantId: string) => ['merchant', merchantId, 'simulation'] as const,
};

export const aiQueryKeys = {
  all: ['ai'] as const,
  insights: (merchantId: string, days: number) => ['ai', merchantId, 'insights', days] as const,
  anomalies: (merchantId: string, days: number) => ['ai', merchantId, 'anomalies', days] as const,
  forecast: (merchantId: string, periods: number) => ['ai', merchantId, 'forecast', periods] as const,
  recommendations: (merchantId: string, status: string) =>
    ['ai', merchantId, 'recommendations', status] as const,
};

// Merchant hooks
export function useMerchantOverview(merchantId: string, days: number = 30) {
  return useQuery({
    queryKey: merchantQueryKeys.overview(merchantId, days),
    queryFn: () => merchantApi.getOverview(merchantId, days),
    staleTime: 60 * 1000, // 1 minute
    retry: 2,
  });
}

export function useMerchantPerformance(merchantId: string, days: number = 30) {
  return useQuery({
    queryKey: merchantQueryKeys.performance(merchantId, days),
    queryFn: () => merchantApi.getPerformance(merchantId, days),
    staleTime: 60 * 1000,
    retry: 2,
  });
}

export function useMerchantCashflow(merchantId: string) {
  return useQuery({
    queryKey: merchantQueryKeys.cashflow(merchantId),
    queryFn: () => merchantApi.getCashflow(merchantId),
    staleTime: 60 * 1000,
    retry: 2,
  });
}

export function useMerchantPeer(merchantId: string) {
  return useQuery({
    queryKey: merchantQueryKeys.peer(merchantId),
    queryFn: () => merchantApi.getPeer(merchantId),
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  });
}

export function useMerchantRisk(merchantId: string, days: number = 30) {
  return useQuery({
    queryKey: merchantQueryKeys.risk(merchantId, days),
    queryFn: () => merchantApi.getRisk(merchantId, days),
    staleTime: 60 * 1000,
    retry: 2,
  });
}

export function useMerchantRecommendation(merchantId: string, days: number = 30) {
  return useQuery({
    queryKey: merchantQueryKeys.recommendation(merchantId, days),
    queryFn: () => merchantApi.getRecommendation(merchantId, days),
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  });
}

export function useMerchantTransactions(
  merchantId: string,
  startDate: string,
  endDate: string,
  limit: number = 100
) {
  return useQuery({
    queryKey: merchantQueryKeys.transactions(merchantId, startDate, endDate),
    queryFn: () => merchantApi.getTransactions(merchantId, startDate, endDate, limit),
    staleTime: 30 * 1000, // 30 seconds
    retry: 2,
  });
}

export function useSimulation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ merchantId, input }: { merchantId: string; input: SimulationInput }) =>
      merchantApi.simulate(merchantId, input),
    onSuccess: (data, { merchantId }) => {
      // Invalidate overview to refresh health score
      queryClient.invalidateQueries({
        queryKey: merchantQueryKeys.overview(merchantId),
      });
    },
  });
}

// AI hooks
export function useAIInsights(merchantId: string, days: number = 30) {
  return useQuery({
    queryKey: aiQueryKeys.insights(merchantId, days),
    queryFn: () => aiApi.getInsights(merchantId, days),
    staleTime: 10 * 60 * 1000, // 10 minutes
    retry: 2,
  });
}

export function useAIAnomalies(merchantId: string, days: number = 30) {
  return useQuery({
    queryKey: aiQueryKeys.anomalies(merchantId, days),
    queryFn: () => aiApi.detectAnomalies(merchantId, days),
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  });
}

export function useAIForecast(merchantId: string, periods: number = 7) {
  return useQuery({
    queryKey: aiQueryKeys.forecast(merchantId, periods),
    queryFn: () => aiApi.getForecast(merchantId, periods),
    staleTime: 10 * 60 * 1000, // 10 minutes
    retry: 2,
  });
}

export function useAIRecommendations(merchantId: string, status: string = 'pending') {
  const queryClient = useQueryClient();

  return useQuery({
    queryKey: aiQueryKeys.recommendations(merchantId, status),
    queryFn: () => aiApi.getRecommendations(merchantId, status),
    staleTime: 5 * 60 * 1000,
    retry: 2,
  });
}

export function useMarkRecommendationImplemented() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (recommendationId: number) =>
      aiApi.markImplemented(recommendationId),
    onSuccess: (data, recommendationId) => {
      // Invalidate recommendations to refresh list
      queryClient.invalidateQueries({
        queryKey: aiQueryKeys.recommendations('MERCHANT001'), // Adjust merchant ID as needed
      });
    },
  });
}

// Default merchant ID for demo
export const DEFAULT_MERCHANT_ID = process.env.NEXT_PUBLIC_MERCHANT_ID || 'MERCHANT001';
