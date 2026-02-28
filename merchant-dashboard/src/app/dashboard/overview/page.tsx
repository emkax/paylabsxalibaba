'use client';

import { useQuery } from '@tanstack/react-query';
import { TrendingUp, TrendingDown, Activity, DollarSign, Repeat, Target } from 'lucide-react';
import styles from './overview.module.css';

// Health Score Gauge Component
function HealthScoreGauge({ score }: { score: number }) {
  const circumference = 2 * Math.PI * 45;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  let colorClass = styles.healthHigh;
  if (score < 70) colorClass = styles.healthLow;
  else if (score < 80) colorClass = styles.healthMedium;

  return (
    <div className={styles.gaugeContainer}>
      <svg className={styles.gauge} viewBox="0 0 100 100">
        <circle
          className={styles.gaugeBackground}
          cx="50"
          cy="50"
          r="45"
          strokeWidth="10"
          fill="none"
        />
        <circle
          className={`${styles.gaugeStroke} ${colorClass}`}
          cx="50"
          cy="50"
          r="45"
          strokeWidth="10"
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          transform="rotate(-90 50 50)"
        />
      </svg>
      <div className={styles.gaugeContent}>
        <span className={styles.gaugeValue}>{score}</span>
        <span className={styles.gaugeLabel}>Health Score</span>
      </div>
    </div>
  );
}

// Survival Probability Component
function SurvivalProbability({ probability }: { probability: number }) {
  return (
    <div className={styles.survivalCard}>
      <div className={styles.survivalHeader}>
        <Target size={20} className={styles.survivalIcon} />
        <span className={styles.survivalLabel}>Survival Probability</span>
      </div>
      <div className={styles.survivalValue}>{probability}%</div>
      <div className={styles.survivalBar}>
        <div
          className={styles.survivalBarFill}
          style={{ width: `${probability}%` }}
        />
      </div>
      <div className={styles.survivalHint}>
        {probability >= 80 ? 'Strong outlook' : probability >= 60 ? 'Moderate outlook' : 'Needs attention'}
      </div>
    </div>
  );
}

// Risk Badge Component
function RiskBadge({ level }: { level: 'low' | 'medium' | 'high' }) {
  const config = {
    low: { label: 'Low Risk', className: styles.badgeSuccess },
    medium: { label: 'Medium Risk', className: styles.badgeWarning },
    high: { label: 'High Risk', className: styles.badgeError },
  };

  return (
    <div className={`${styles.riskBadge} ${config[level].className}`}>
      {config[level].label}
    </div>
  );
}

// KPI Card Component
function KPICard({
  title,
  value,
  change,
  icon: Icon,
  format = 'number',
}: {
  title: string;
  value: number;
  change?: number;
  icon: React.ComponentType<{ size?: number }>;
  format?: 'number' | 'percent' | 'currency';
}) {
  const formatValue = () => {
    if (format === 'currency') {
      return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
      }).format(value);
    }
    if (format === 'percent') {
      return `${value.toFixed(1)}%`;
    }
    if (value >= 1000000) {
      return `${(value / 1000000).toFixed(1)}M`;
    }
    return value.toLocaleString('id-ID');
  };

  return (
    <div className={styles.kpiCard}>
      <div className={styles.kpiHeader}>
        <span className={styles.kpiTitle}>{title}</span>
        <span className={styles.kpiIcon}><Icon size={20} /></span>
      </div>
      <div className={styles.kpiValue}>{formatValue()}</div>
      {change !== undefined && (
        <div className={`${styles.kpiChange} ${change >= 0 ? styles.kpiChangePositive : styles.kpiChangeNegative}`}>
          {change >= 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
          <span>{change >= 0 ? '+' : ''}{change.toFixed(1)}%</span>
        </div>
      )}
    </div>
  );
}

export default function OverviewPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['overview', '010614'],
    queryFn: async () => {
      const response = await fetch('/api/merchant/010614?type=overview');
      if (!response.ok) throw new Error('Failed to fetch');
      return response.json();
    },
  });

  if (isLoading) {
    return (
      <div className={styles.loadingContainer}>
        <div className={styles.skeletonGauge} />
        <div className={styles.skeletonCards}>
          {[...Array(6)].map((_, i) => (
            <div key={i} className={styles.skeletonKpi} />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.errorContainer}>
        <p>Failed to load dashboard data. Please try again.</p>
      </div>
    );
  }

  const overview = data.data;

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Dashboard Overview</h1>
          <p className={styles.subtitle}>Merchant Health Intelligence</p>
        </div>
        <RiskBadge level={overview.riskLevel} />
      </div>

      <div className={styles.mainGrid}>
        <div className={styles.healthSection}>
          <HealthScoreGauge score={overview.healthScore} />
        </div>
        <div className={styles.survivalSection}>
          <SurvivalProbability probability={overview.survivalProbability} />
        </div>
      </div>

      <div className={styles.kpiGrid}>
        <KPICard
          title="Total Revenue"
          value={overview.kpis.revenue}
          change={overview.kpis.revenueChange}
          icon={DollarSign}
          format="currency"
        />
        <KPICard
          title="Volatility Score"
          value={overview.kpis.volatilityScore}
          icon={Activity}
          format="number"
        />
        <KPICard
          title="Cashflow Stress"
          value={overview.kpis.cashflowStressIndex}
          icon={TrendingDown}
          format="number"
        />
        <KPICard
          title="Peer Percentile"
          value={overview.kpis.peerPercentile}
          icon={Target}
          format="percent"
        />
        <KPICard
          title="Repeat Ratio"
          value={overview.kpis.repeatRatio * 100}
          icon={Repeat}
          format="percent"
        />
        <KPICard
          title="Revenue Change"
          value={overview.kpis.revenueChange}
          icon={TrendingUp}
          format="percent"
        />
      </div>

      <div className={styles.footer}>
        <span className={styles.lastUpdated}>
          Last updated: {new Date(overview.lastUpdated).toLocaleString('id-ID')}
        </span>
      </div>
    </div>
  );
}
