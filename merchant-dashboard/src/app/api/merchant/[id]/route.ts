import { NextResponse } from 'next/server';
import {
  generateOverviewData,
  generateRevenueData,
  generateCashflowData,
  generatePeerData,
  generateRecommendationData,
  generateSimulationOutput,
} from '@/lib/mock-data';

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const { searchParams } = new URL(request.url);
  const type = searchParams.get('type');

  try {
    let data;

    switch (type) {
      case 'overview':
        data = generateOverviewData(id);
        break;
      case 'performance':
        const days = parseInt(searchParams.get('days') || '30');
        data = generateRevenueData(days);
        break;
      case 'cashflow':
        data = generateCashflowData();
        break;
      case 'peer':
        data = generatePeerData();
        break;
      case 'risk':
        const overview = generateOverviewData(id);
        data = {
          riskLevel: overview.riskLevel,
          riskScore: 100 - overview.healthScore,
          factors: [
            { name: 'Revenue Volatility', score: overview.kpis.volatilityScore },
            { name: 'Cashflow Stress', score: overview.kpis.cashflowStressIndex },
            { name: 'Peer Position', score: 100 - overview.kpis.peerPercentile },
          ],
        };
        break;
      case 'recommendation':
        data = generateRecommendationData();
        break;
      default:
        return NextResponse.json({ error: 'Invalid type' }, { status: 400 });
    }

    return NextResponse.json({
      data,
      lastUpdated: new Date().toISOString(),
    });
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
