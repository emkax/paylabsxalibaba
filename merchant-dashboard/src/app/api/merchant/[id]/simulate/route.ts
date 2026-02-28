import { NextResponse } from 'next/server';
import { generateSimulationOutput } from '@/lib/mock-data';

export async function POST(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;

  try {
    const body = await request.json();

    const simulationInput = {
      discountPercentage: body.discountPercentage ?? 0,
      costReduction: body.costReduction ?? 0,
      marketingBoost: body.marketingBoost ?? 0,
      deliveryIntegration: body.deliveryIntegration ?? false,
    };

    const result = generateSimulationOutput(simulationInput);

    return NextResponse.json({
      data: result,
      lastUpdated: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Simulation API Error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
