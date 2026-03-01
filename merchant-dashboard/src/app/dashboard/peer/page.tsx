'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { Users, Trophy, TrendingUp } from 'lucide-react';
import styles from './peer.module.css';

type PeerSegment = 'city' | 'revenue' | 'category';

export default function PeerBenchmarkPage() {
  const [segment, setSegment] = useState<PeerSegment>('city');

  const { data, isLoading } = useQuery({
    queryKey: ['peer', segment],
    queryFn: async () => {
      const response = await fetch('/api/merchant/010614?type=peer');
      if (!response.ok) throw new Error('Failed to fetch');
      return response.json();
    },
  });

  if (isLoading) {
    return (
      <div className={styles.loadingContainer}>
        <div className={styles.skeletonGrid}>
          <div className={styles.skeletonGauge} />
          <div className={styles.skeletonRadar} />
        </div>
        <div className={styles.skeletonTable} />
      </div>
    );
  }

  const peerData = data.data;

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Peer Benchmark</h1>
          <p className={styles.subtitle}>Compare your performance with industry peers</p>
        </div>
        <div className={styles.segmentToggle}>
          <button
            className={`${styles.segmentBtn} ${segment === 'city' ? styles.active : ''}`}
            onClick={() => setSegment('city')}
          >
            By City
          </button>
          <button
            className={`${styles.segmentBtn} ${segment === 'revenue' ? styles.active : ''}`}
            onClick={() => setSegment('revenue')}
          >
            By Revenue
          </button>
          <button
            className={`${styles.segmentBtn} ${segment === 'category' ? styles.active : ''}`}
            onClick={() => setSegment('category')}
          >
            By Category
          </button>
        </div>
      </div>

      <div className={styles.mainGrid}>
        {/* Percentile Gauge */}
        <div className={styles.gaugeCard}>
          <div className={styles.gaugeHeader}>
            <Trophy size={20} className={styles.gaugeIcon} />
            <span className={styles.gaugeLabel}>Your Percentile Rank</span>
          </div>
          <div className={styles.gaugeContainer}>
            <svg className={styles.gauge} viewBox="0 0 100 100">
              <defs>
                <linearGradient id="percentileGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#4285f4" />
                  <stop offset="100%" stopColor="#34a853" />
                </linearGradient>
              </defs>
              <circle
                className={styles.gaugeBackground}
                cx="50"
                cy="50"
                r="45"
                strokeWidth="12"
                fill="none"
                strokeLinecap="round"
              />
              <circle
                className={styles.gaugeStroke}
                cx="50"
                cy="50"
                r="45"
                strokeWidth="12"
                fill="none"
                strokeLinecap="round"
                style={{
                  strokeDasharray: `${2 * Math.PI * 45}`,
                  strokeDashoffset: `${2 * Math.PI * 45 * (1 - peerData.percentile / 100)}`,
                  transform: 'rotate(-90deg)',
                  transformOrigin: '50% 50%',
                }}
              />
            </svg>
            <div className={styles.gaugeContent}>
              <span className={styles.gaugeValue}>{peerData.percentile}</span>
              <span className={styles.gaugeUnit}>th percentile</span>
            </div>
          </div>
          <div className={styles.gaugeInterpretation}>
            You're performing better than <strong>{peerData.percentile}%</strong> of peers in this segment
          </div>
        </div>

        {/* Radar Chart */}
        <div className={styles.radarCard}>
          <div className={styles.radarHeader}>
            <Users size={20} className={styles.radarIcon} />
            <span className={styles.radarLabel}>Multi-Metric Comparison</span>
          </div>
          <div className={styles.radar}>
            <ResponsiveContainer width="100%" height={350}>
              <RadarChart data={peerData.radarData}>
                <PolarGrid stroke="#e0e0e0" />
                <PolarAngleAxis
                  dataKey="metric"
                  tick={{ fontSize: 12, fill: 'var(--foreground)' }}
                />
                <PolarRadiusAxis
                  angle={90}
                  domain={[0, 100]}
                  tick={{ fontSize: 10 }}
                  tickFormatter={(value) => `${value}%`}
                />
                <Legend />
                <Radar
                  name="You"
                  dataKey="merchant"
                  stroke="#4285f4"
                  fill="#4285f4"
                  fillOpacity={0.3}
                />
                <Radar
                  name="Peers Avg"
                  dataKey="peers"
                  stroke="#ea4335"
                  fill="#ea4335"
                  fillOpacity={0.2}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Comparison Table */}
      <div className={styles.tableCard}>
        <div className={styles.tableHeader}>
          <h2 className={styles.tableTitle}>Detailed Comparison</h2>
          <TrendingUp size={20} className={styles.tableIcon} />
        </div>
        <div className={styles.tableWrapper}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th className={styles.tableTh}>Metric</th>
                <th className={`${styles.tableTh} ${styles.yourColumn}`}>Your Performance</th>
                <th className={styles.tableTh}>Peer Average</th>
                <th className={styles.tableTh}>Industry Average</th>
                <th className={styles.tableTh}>vs Peers</th>
              </tr>
            </thead>
            <tbody>
              {peerData.comparisonTable.map((row: any, index: number) => {
                const vsPeers = row.metric.includes('Rate') || row.metric.includes('Retention') || row.metric.includes('%')
                  ? ((row.merchant - row.peers) / row.peers * 100).toFixed(1) + '%'
                  : ((row.merchant - row.peers) / row.peers * 100).toFixed(1) + '%';
                const isPositive = parseFloat(vsPeers) >= 0;

                return (
                  <tr key={index} className={styles.tableRow}>
                    <td className={styles.tableTd}>{row.metric}</td>
                    <td className={`${styles.tableTd} ${styles.yourColumn}`}>
                      <span className={styles.yourValue}>{row.merchant.toLocaleString()}</span>
                    </td>
                    <td className={styles.tableTd}>{row.peers.toLocaleString()}</td>
                    <td className={styles.tableTd}>{row.industry.toLocaleString()}</td>
                    <td className={styles.tableTd}>
                      <span className={`${styles.vsBadge} ${isPositive ? styles.vsPositive : styles.vsNegative}`}>
                        {isPositive ? '+' : ''}{vsPeers}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Peer Insights */}
      <div className={styles.insightsGrid}>
        <div className={styles.insightCard}>
          <div className={styles.insightIconPositive}>
            <TrendingUp size={20} />
          </div>
          <div className={styles.insightContent}>
            <div className={styles.insightTitle}>Strengths</div>
            <div className={styles.insightText}>
              {peerData.radarData
                .filter((item: any) => item.merchant > item.peers)
                .map((item: any) => item.metric)
                .slice(0, 2)
                .join(', ') || 'Area for improvement'}
            </div>
          </div>
        </div>
        <div className={styles.insightCard}>
          <div className={styles.insightIconNeutral}>
            <TrendingUp size={20} style={{ transform: 'rotate(180deg)' }} />
          </div>
          <div className={styles.insightContent}>
            <div className={styles.insightTitle}>Opportunities</div>
            <div className={styles.insightText}>
              {peerData.radarData
                .filter((item: any) => item.merchant < item.peers)
                .map((item: any) => item.metric)
                .slice(0, 2)
                .join(', ') || 'No significant gaps'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
