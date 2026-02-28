'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { TrendingUp, TrendingDown, Wallet, AlertTriangle } from 'lucide-react';
import styles from './cashflow.module.css';

export default function CashflowPage() {
  const [costReduction, setCostReduction] = useState(0);

  const { data, isLoading } = useQuery({
    queryKey: ['cashflow'],
    queryFn: async () => {
      const response = await fetch('/api/merchant/010614?type=cashflow');
      if (!response.ok) throw new Error('Failed to fetch');
      return response.json();
    },
  });

  if (isLoading) {
    return (
      <div className={styles.loadingContainer}>
        <div className={styles.skeletonChart} />
        <div className={styles.skeletonCards} />
      </div>
    );
  }

  const cashflowData = data.data;

  // Combine inflow and outflow for chart
  const chartData = cashflowData.inflow.map((item: any, index: number) => ({
    date: item.date.slice(5),
    inflow: item.amount / 1000000,
    outflow: cashflowData.outflow[index].amount / 1000000,
    net: (item.amount - cashflowData.outflow[index].amount) / 1000000,
  }));

  // Calculate scenario with cost reduction
  const reducedOutflow = cashflowData.outflow.map((item: any) => ({
    ...item,
    amount: item.amount * (1 - costReduction / 100),
  }));

  const projectedRunway = costReduction > 0
    ? Math.floor(cashflowData.liquidityRunway * (1 + costReduction / 100))
    : cashflowData.liquidityRunway;

  const getNetColor = (value: number) => {
    return value >= 0 ? '#188038' : '#d93025';
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className={styles.tooltip}>
          <p className={styles.tooltipLabel}>{label}</p>
          <p className={styles.tooltipItem} style={{ color: '#4285f4' }}>
            Inflow: {(payload[0].value / 1).toFixed(2)}M
          </p>
          <p className={styles.tooltipItem} style={{ color: '#ea4335' }}>
            Outflow: {(payload[1].value / 1).toFixed(2)}M
          </p>
          <p className={styles.tooltipItem} style={{ color: getNetColor(payload[2].value) }}>
            Net: {(payload[2].value / 1).toFixed(2)}M
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Cashflow Monitoring</h1>
          <p className={styles.subtitle}>Track inflows, outflows, and liquidity</p>
        </div>
      </div>

      {/* Key Metrics */}
      <div className={styles.metricsGrid}>
        <div className={`${styles.metricCard} ${cashflowData.negativeStreak > 0 ? styles.warning : ''}`}>
          <div className={styles.metricHeader}>
            <Wallet size={20} className={styles.metricIcon} />
            <span className={styles.metricLabel}>Liquidity Runway</span>
          </div>
          <div className={styles.metricValue}>
            {cashflowData.liquidityRunway} <span className={styles.metricUnit}>days</span>
          </div>
          <div className={styles.metricProgress}>
            <div
              className={styles.metricProgressBar}
              style={{
                width: `${Math.min(100, (cashflowData.liquidityRunway / cashflowData.runwayTarget) * 100)}%`,
                background: cashflowData.liquidityRunway >= cashflowData.runwayTarget
                  ? 'var(--success)'
                  : cashflowData.liquidityRunway >= cashflowData.runwayTarget / 2
                  ? 'var(--warning)'
                  : 'var(--error)',
              }}
            />
          </div>
          <div className={styles.metricTarget}>
            Target: {cashflowData.runwayTarget} days
          </div>
        </div>

        <div className={`${styles.metricCard} ${cashflowData.negativeStreak >= 3 ? styles.warning : ''}`}>
          <div className={styles.metricHeader}>
            <TrendingDown size={20} className={styles.metricIcon} />
            <span className={styles.metricLabel}>Negative Streak</span>
          </div>
          <div className={styles.metricValue}>
            {cashflowData.negativeStreak} <span className={styles.metricUnit}>days</span>
          </div>
          {cashflowData.negativeStreak >= 3 && (
            <div className={styles.metricWarning}>
              <AlertTriangle size={14} />
              <span>Extended negative cashflow detected</span>
            </div>
          )}
        </div>

        <div className={styles.metricCard}>
          <div className={styles.metricHeader}>
            <TrendingUp size={20} className={styles.metricIcon} />
            <span className={styles.metricLabel}>Avg Daily Inflow</span>
          </div>
          <div className={styles.metricValue}>
            {(cashflowData.inflow.reduce((acc: number, item: any) => acc + item.amount, 0) / 30 / 1000000).toFixed(2)}M
          </div>
        </div>

        <div className={styles.metricCard}>
          <div className={styles.metricHeader}>
            <Wallet size={20} className={styles.metricIcon} />
            <span className={styles.metricLabel}>Avg Daily Outflow</span>
          </div>
          <div className={styles.metricValue}>
            {(cashflowData.outflow.reduce((acc: number, item: any) => acc + item.amount, 0) / 30 / 1000000).toFixed(2)}M
          </div>
        </div>
      </div>

      {/* Inflow vs Outflow Chart */}
      <div className={styles.chartCard}>
        <div className={styles.chartHeader}>
          <h2 className={styles.chartTitle}>Inflow vs Outflow</h2>
        </div>
        <div className={styles.chart}>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 12 }}
                interval={Math.floor(chartData.length / 15)}
              />
              <YAxis
                tick={{ fontSize: 12 }}
                tickFormatter={(value) => `${value}M`}
              />
              <Tooltip content={CustomTooltip} />
              <Legend />
              <Bar dataKey="inflow" fill="#4285f4" radius={[4, 4, 0, 0]} name="Inflow" />
              <Bar dataKey="outflow" fill="#ea4335" radius={[4, 4, 0, 0]} name="Outflow" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Net Cashflow Chart */}
      <div className={styles.chartCard}>
        <div className={styles.chartHeader}>
          <h2 className={styles.chartTitle}>Net Cashflow</h2>
        </div>
        <div className={styles.chart}>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 12 }}
                interval={Math.floor(chartData.length / 15)}
              />
              <YAxis
                tick={{ fontSize: 12 }}
                tickFormatter={(value) => `${value}M`}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--surface-elevated)',
                  border: '1px solid var(--border)',
                  borderRadius: '8px',
                }}
                formatter={(value: number | undefined) => [`${(value ?? 0).toFixed(2)}M IDR`, 'Net Cashflow' as const]}
              />
              <Bar dataKey="net" radius={[4, 4, 0, 0]} name="Net">
                {chartData.map((entry: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={getNetColor(entry.net)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Cost Reduction Scenario */}
      <div className={styles.scenarioCard}>
        <div className={styles.scenarioHeader}>
          <h2 className={styles.scenarioTitle}>Cost Reduction Scenario</h2>
          <div className={styles.scenarioValue}>
            {costReduction}% reduction
          </div>
        </div>
        <div className={styles.scenarioContent}>
          <div className={styles.sliderContainer}>
            <input
              type="range"
              min="0"
              max="30"
              value={costReduction}
              onChange={(e) => setCostReduction(parseInt(e.target.value))}
              className={styles.slider}
            />
            <div className={styles.sliderMarks}>
              <span>0%</span>
              <span>10%</span>
              <span>20%</span>
              <span>30%</span>
            </div>
          </div>
          <div className={styles.scenarioResults}>
            <div className={styles.resultCard}>
              <div className={styles.resultLabel}>Current Runway</div>
              <div className={styles.resultValue}>{cashflowData.liquidityRunway} days</div>
            </div>
            <div className={styles.resultArrow}>→</div>
            <div className={styles.resultCard}>
              <div className={styles.resultLabel}>Projected Runway</div>
              <div className={styles.resultValuePositive}>{projectedRunway} days</div>
            </div>
            <div className={styles.resultCard}>
              <div className={styles.resultLabel}>Improvement</div>
              <div className={styles.resultValuePositive}>+{projectedRunway - cashflowData.liquidityRunway} days</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
