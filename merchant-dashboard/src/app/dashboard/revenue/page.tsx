'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceDot,
} from 'recharts';
import { Download, Calendar, TrendingUp } from 'lucide-react';
import styles from './revenue.module.css';

type DaysOption = 30 | 60 | 90;

export default function RevenuePage() {
  const [days, setDays] = useState<DaysOption>(30);

  const { data, isLoading } = useQuery({
    queryKey: ['revenue', days],
    queryFn: async () => {
      const response = await fetch(`/api/merchant/010614?type=performance&days=${days}`);
      if (!response.ok) throw new Error('Failed to fetch');
      return response.json();
    },
  });

  const handleExport = () => {
    // Mock export functionality
    alert('CSV export would download here');
  };

  if (isLoading) {
    return (
      <div className={styles.loadingContainer}>
        <div className={styles.skeletonChart} />
        <div className={styles.skeletonChart} />
      </div>
    );
  }

  const revenueData = data.data;

  // Format data for charts
  const lineChartData = revenueData.dailyRevenue.map((item: any) => ({
    ...item,
    date: item.date.slice(5), // MM-DD format
    revenue: item.revenue / 1000000, // Convert to millions
    forecast: item.forecast ? item.forecast / 1000000 : null,
  }));

  const barChartData = revenueData.transactionFrequency.map((item: any) => ({
    ...item,
    date: item.date.slice(5),
  }));

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Revenue Analytics</h1>
          <p className={styles.subtitle}>Transaction performance and trends</p>
        </div>
        <div className={styles.headerActions}>
          <div className={styles.dateRange}>
            <button
              className={`${styles.rangeBtn} ${days === 30 ? styles.active : ''}`}
              onClick={() => setDays(30)}
            >
              30D
            </button>
            <button
              className={`${styles.rangeBtn} ${days === 60 ? styles.active : ''}`}
              onClick={() => setDays(60)}
            >
              60D
            </button>
            <button
              className={`${styles.rangeBtn} ${days === 90 ? styles.active : ''}`}
              onClick={() => setDays(90)}
            >
              90D
            </button>
          </div>
          <button className={styles.exportBtn} onClick={handleExport}>
            <Download size={18} />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* Summary Stats */}
      <div className={styles.statsGrid}>
        <div className={styles.statCard}>
          <div className={styles.statLabel}>Total Revenue</div>
          <div className={styles.statValue}>
            {new Intl.NumberFormat('id-ID', {
              style: 'currency',
              currency: 'IDR',
              minimumFractionDigits: 0,
              maximumFractionDigits: 0,
            }).format(revenueData.dailyRevenue.reduce((acc: number, item: any) => acc + item.revenue, 0))}
          </div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statLabel}>Total Transactions</div>
          <div className={styles.statValue}>{revenueData.totalTransactions.toLocaleString()}</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statLabel}>Avg Transaction Value</div>
          <div className={styles.statValue}>
            {new Intl.NumberFormat('id-ID', {
              style: 'currency',
              currency: 'IDR',
              minimumFractionDigits: 0,
            }).format(revenueData.averageTransactionValue)}
          </div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statLabel}>Daily Average</div>
          <div className={styles.statValue}>
            {new Intl.NumberFormat('id-ID', {
              style: 'currency',
              currency: 'IDR',
              minimumFractionDigits: 0,
            }).format(revenueData.dailyRevenue.reduce((acc: number, item: any) => acc + item.revenue, 0) / days)}
          </div>
        </div>
      </div>

      {/* Revenue Line Chart */}
      <div className={styles.chartCard}>
        <div className={styles.chartHeader}>
          <h2 className={styles.chartTitle}>
            <TrendingUp size={20} />
            Revenue Trend
          </h2>
          <span className={styles.chartLegend}>
            <span className={styles.legendDotActual}></span> Actual
            <span className={styles.legendDotForecast}></span> Forecast
          </span>
        </div>
        <div className={styles.chart}>
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={lineChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 12 }}
                interval={Math.floor(lineChartData.length / 10)}
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
                formatter={(value: number | undefined) => [
                  `${(value ?? 0).toFixed(2)}M IDR`,
                  'Revenue' as const,
                ]}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="revenue"
                stroke="#4285f4"
                strokeWidth={2}
                dot={(props: any) => {
                  const { cx, cy, payload } = props;
                  if (payload.isAnomaly) {
                    return (
                      <circle cx={cx} cy={cy} r={5} fill="#d93025" stroke="#fff" strokeWidth={2} />
                    );
                  }
                  return null;
                }}
                name="Revenue"
              />
              <Line
                type="monotone"
                dataKey="forecast"
                stroke="#34a853"
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={false}
                name="Forecast"
              />
              {lineChartData.filter((d: any) => d.isAnomaly).length > 0 && (
                <ReferenceDot
                  x={lineChartData.find((d: any) => d.isAnomaly)?.date}
                  y={lineChartData.find((d: any) => d.isAnomaly)?.revenue}
                  r={6}
                  fill="#d93025"
                  stroke="#fff"
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        </div>
        {revenueData.dailyRevenue.some((item: any) => item.isAnomaly) && (
          <div className={styles.anomalyNote}>
            <span className={styles.anomalyDot}></span>
            Red dots indicate anomalous days (significant revenue drops)
          </div>
        )}
      </div>

      {/* Transaction Frequency Chart */}
      <div className={styles.chartCard}>
        <div className={styles.chartHeader}>
          <h2 className={styles.chartTitle}>
            <Calendar size={20} />
            Transaction Frequency
          </h2>
        </div>
        <div className={styles.chart}>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={barChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 12 }}
                interval={Math.floor(barChartData.length / 15)}
              />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--surface-elevated)',
                  border: '1px solid var(--border)',
                  borderRadius: '8px',
                }}
              />
              <Bar dataKey="count" fill="#1a73e8" radius={[4, 4, 0, 0]} name="Transactions" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
