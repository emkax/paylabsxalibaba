'use client';

import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Lightbulb, AlertTriangle, CheckCircle, Clock, Target, TrendingUp } from 'lucide-react';
import styles from './recommendation.module.css';

interface ActionItem {
  id: string;
  title: string;
  description: string;
  expectedImpact: string;
  status: 'pending' | 'implemented';
  priority: 'high' | 'medium' | 'low';
}

export default function RecommendationPage() {
  const [actionItems, setActionItems] = useState<ActionItem[]>([]);

  const { data, isLoading } = useQuery({
    queryKey: ['recommendations'],
    queryFn: async () => {
      const response = await fetch('/api/merchant/010614?type=recommendation');
      if (!response.ok) throw new Error('Failed to fetch');
      return response.json();
    },
  });

  // Initialize action items when data loads
  useEffect(() => {
    if (data) {
      const allActions = [
        ...data.data.immediateActions,
        ...data.data.strategicActions,
      ];
      setActionItems(allActions);
    }
  }, [data]);

  const toggleStatus = (id: string) => {
    setActionItems(prev =>
      prev.map(item =>
        item.id === id
          ? { ...item, status: item.status === 'pending' ? 'implemented' : 'pending' }
          : item
      )
    );
  };

  if (isLoading) {
    return (
      <div className={styles.loadingContainer}>
        <div className={styles.skeletonSection}>
          <div className={styles.skeletonTitle} />
          <div className={styles.skeletonCauses} />
        </div>
        <div className={styles.skeletonActions} />
      </div>
    );
  }

  const recommendations = data.data;
  const implementedCount = actionItems.filter(a => a.status === 'implemented').length;
  const totalActions = actionItems.length;

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return styles.priorityHigh;
      case 'medium': return styles.priorityMedium;
      case 'low': return styles.priorityLow;
      default: return '';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return styles.severityHigh;
      case 'medium': return styles.severityMedium;
      case 'low': return styles.severityLow;
      default: return '';
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>AI Recommendations</h1>
          <p className={styles.subtitle}>Data-driven insights to improve your business health</p>
        </div>
        <div className={styles.progressCard}>
          <div className={styles.progressHeader}>
            <CheckCircle size={18} className={styles.progressIcon} />
            <span className={styles.progressLabel}>Actions Completed</span>
          </div>
          <div className={styles.progressValue}>
            {implementedCount} / {totalActions}
          </div>
          <div className={styles.progressBar}>
            <div
              className={styles.progressFill}
              style={{ width: `${(implementedCount / totalActions) * 100}%` }}
            />
          </div>
        </div>
      </div>

      {/* Root Cause Analysis */}
      <div className={styles.section}>
        <div className={styles.sectionHeader}>
          <AlertTriangle size={20} className={styles.sectionIcon} />
          <h2 className={styles.sectionTitle}>Root Cause Analysis</h2>
        </div>
        <div className={styles.causesGrid}>
          {recommendations.rootCauses.map((cause: any, index: number) => (
            <div key={index} className={`${styles.causeCard} ${getSeverityColor(cause.severity)}`}>
              <div className={styles.causeHeader}>
                <span className={styles.causeSeverity}>{cause.severity.toUpperCase()}</span>
                <AlertTriangle size={18} />
              </div>
              <h3 className={styles.causeTitle}>{cause.title}</h3>
              <p className={styles.causeDescription}>{cause.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Expected Impact */}
      <div className={styles.section}>
        <div className={styles.sectionHeader}>
          <Target size={20} className={styles.sectionIcon} />
          <h2 className={styles.sectionTitle}>Expected Impact</h2>
        </div>
        <div className={styles.impactGrid}>
          <div className={styles.impactCard}>
            <div className={styles.impactIcon}>
              <TrendingUp size={24} />
            </div>
            <div className={styles.impactValue}>+{recommendations.expectedImpact.revenue}%</div>
            <div className={styles.impactLabel}>Revenue Increase</div>
          </div>
          <div className={styles.impactCard}>
            <div className={styles.impactIcon}>
              <Lightbulb size={24} />
            </div>
            <div className={styles.impactValue}>+{recommendations.expectedImpact.healthScore}</div>
            <div className={styles.impactLabel}>Health Score Points</div>
          </div>
        </div>
      </div>

      {/* Immediate Actions (30 days) */}
      <div className={styles.section}>
        <div className={styles.sectionHeader}>
          <Clock size={20} className={styles.sectionIcon} />
          <h2 className={styles.sectionTitle}>Immediate Actions (30 days)</h2>
        </div>
        <div className={styles.actionsList}>
          {actionItems
            .filter(a => recommendations.immediateActions.some((ia: any) => ia.id === a.id))
            .map((action) => (
              <div key={action.id} className={styles.actionCard}>
                <div className={styles.actionContent}>
                  <div className={styles.actionHeader}>
                    <div className={styles.actionTitleRow}>
                      <span className={`${styles.priorityBadge} ${getPriorityColor(action.priority)}`}>
                        {action.priority.toUpperCase()}
                      </span>
                      <h3 className={styles.actionTitle}>{action.title}</h3>
                    </div>
                    <button
                      className={`${styles.toggleBtn} ${action.status === 'implemented' ? styles.implemented : ''}`}
                      onClick={() => toggleStatus(action.id)}
                    >
                      {action.status === 'implemented' ? (
                        <>
                          <CheckCircle size={16} />
                          <span>Implemented</span>
                        </>
                      ) : (
                        <>
                          <Clock size={16} />
                          <span>Mark Done</span>
                        </>
                      )}
                    </button>
                  </div>
                  <p className={styles.actionDescription}>{action.description}</p>
                  <div className={styles.actionImpact}>
                    <span className={styles.impactLabel}>Expected Impact:</span>
                    <span className={styles.impactValue}>{action.expectedImpact}</span>
                  </div>
                </div>
              </div>
            ))}
        </div>
      </div>

      {/* Strategic Actions (90 days) */}
      <div className={styles.section}>
        <div className={styles.sectionHeader}>
          <Target size={20} className={styles.sectionIcon} />
          <h2 className={styles.sectionTitle}>Strategic Actions (90 days)</h2>
        </div>
        <div className={styles.actionsList}>
          {actionItems
            .filter(a => recommendations.strategicActions.some((sa: any) => sa.id === a.id))
            .map((action) => (
              <div key={action.id} className={styles.actionCard}>
                <div className={styles.actionContent}>
                  <div className={styles.actionHeader}>
                    <div className={styles.actionTitleRow}>
                      <span className={`${styles.priorityBadge} ${getPriorityColor(action.priority)}`}>
                        {action.priority.toUpperCase()}
                      </span>
                      <h3 className={styles.actionTitle}>{action.title}</h3>
                    </div>
                    <button
                      className={`${styles.toggleBtn} ${action.status === 'implemented' ? styles.implemented : ''}`}
                      onClick={() => toggleStatus(action.id)}
                    >
                      {action.status === 'implemented' ? (
                        <>
                          <CheckCircle size={16} />
                          <span>Implemented</span>
                        </>
                      ) : (
                        <>
                          <Clock size={16} />
                          <span>Mark Done</span>
                        </>
                      )}
                    </button>
                  </div>
                  <p className={styles.actionDescription}>{action.description}</p>
                  <div className={styles.actionImpact}>
                    <span className={styles.impactLabel}>Expected Impact:</span>
                    <span className={styles.impactValue}>{action.expectedImpact}</span>
                  </div>
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
}
