'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Sliders, TrendingUp, Activity, Target, Truck } from 'lucide-react';
import styles from './simulation.module.css';

export default function SimulationPage() {
  const [discountPercentage, setDiscountPercentage] = useState(10);
  const [costReduction, setCostReduction] = useState(10);
  const [marketingBoost, setMarketingBoost] = useState(10);
  const [deliveryIntegration, setDeliveryIntegration] = useState(false);

  const { data: simulationData, mutate } = useMutation({
    mutationFn: async (input: any) => {
      const response = await fetch('/api/merchant/010614/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(input),
      });
      if (!response.ok) throw new Error('Failed to simulate');
      return response.json();
    },
  });

  // Trigger simulation whenever inputs change
  useState(() => {
    mutate({
      discountPercentage,
      costReduction,
      marketingBoost,
      deliveryIntegration,
    });
  });

  const baseHealthScore = 75;
  const baseSurvivalProbability = 82;
  const baseRevenue = 156; // in millions

  // Calculate live preview values
  const discountImpact = discountPercentage * 0.8;
  const costReductionImpact = costReduction * 1.2;
  const marketingImpact = marketingBoost * 0.6;
  const deliveryImpact = deliveryIntegration ? 15 : 0;

  const revenueImpact = discountImpact + marketingImpact + deliveryImpact;
  const healthImpact = costReductionImpact + revenueImpact * 0.3;
  const survivalImpact = healthImpact * 0.8;

  const forecastedRevenue = Math.floor(baseRevenue * (1 + revenueImpact / 100));
  const updatedHealthScore = Math.min(100, Math.floor(baseHealthScore + healthImpact));
  const updatedSurvivalProbability = Math.min(100, Math.floor(baseSurvivalProbability + survivalImpact));

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>What-If Simulation</h1>
          <p className={styles.subtitle}>Model different scenarios and see their impact on your business</p>
        </div>
      </div>

      <div className={styles.mainGrid}>
        {/* Controls Panel */}
        <div className={styles.controlsCard}>
          <div className={styles.controlsHeader}>
            <Sliders size={20} className={styles.controlsIcon} />
            <h2 className={styles.controlsTitle}>Adjust Variables</h2>
          </div>

          {/* Discount Slider */}
          <div className={styles.controlGroup}>
            <div className={styles.controlHeader}>
              <div className={styles.controlLabel}>
                <TrendingUp size={18} />
                <span>Discount Percentage</span>
              </div>
              <span className={styles.controlValue}>{discountPercentage}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="50"
              value={discountPercentage}
              onChange={(e) => setDiscountPercentage(parseInt(e.target.value))}
              className={styles.slider}
            />
            <div className={styles.sliderMarks}>
              <span>0%</span>
              <span>25%</span>
              <span>50%</span>
            </div>
            <p className={styles.controlHint}>
              Higher discounts may increase revenue but reduce margins
            </p>
          </div>

          {/* Cost Reduction Slider */}
          <div className={styles.controlGroup}>
            <div className={styles.controlHeader}>
              <div className={styles.controlLabel}>
                <Activity size={18} />
                <span>Cost Reduction</span>
              </div>
              <span className={styles.controlValue}>{costReduction}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="40"
              value={costReduction}
              onChange={(e) => setCostReduction(parseInt(e.target.value))}
              className={styles.slider}
            />
            <div className={styles.sliderMarks}>
              <span>0%</span>
              <span>20%</span>
              <span>40%</span>
            </div>
            <p className={styles.controlHint}>
              Reduce operational costs through efficiency improvements
            </p>
          </div>

          {/* Marketing Boost Slider */}
          <div className={styles.controlGroup}>
            <div className={styles.controlHeader}>
              <div className={styles.controlLabel}>
                <Target size={18} />
                <span>Marketing Boost</span>
              </div>
              <span className={styles.controlValue}>{marketingBoost}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={marketingBoost}
              onChange={(e) => setMarketingBoost(parseInt(e.target.value))}
              className={styles.slider}
            />
            <div className={styles.sliderMarks}>
              <span>0%</span>
              <span>50%</span>
              <span>100%</span>
            </div>
            <p className={styles.controlHint}>
              Increase marketing spend to drive customer acquisition
            </p>
          </div>

          {/* Delivery Integration Toggle */}
          <div className={styles.controlGroup}>
            <div className={styles.controlHeader}>
              <div className={styles.controlLabel}>
                <Truck size={18} />
                <span>Delivery Platform Integration</span>
              </div>
              <button
                className={`${styles.toggle} ${deliveryIntegration ? styles.toggleOn : ''}`}
                onClick={() => setDeliveryIntegration(!deliveryIntegration)}
              >
                <span className={styles.toggleKnob}></span>
              </button>
            </div>
            <p className={styles.controlHint}>
              Integrate with GoFood, GrabFood, ShopeeFood for expanded reach
            </p>
          </div>
        </div>

        {/* Results Panel */}
        <div className={styles.resultsCard}>
          <div className={styles.resultsHeader}>
            <h2 className={styles.resultsTitle}>Projected Impact</h2>
          </div>

          {/* Health Score Result */}
          <div className={styles.resultSection}>
            <div className={styles.resultLabel}>Health Score</div>
            <div className={styles.resultComparison}>
              <div className={styles.resultBase}>{baseHealthScore}</div>
              <div className={styles.resultArrow}>→</div>
              <div className={styles.resultProjected}>{updatedHealthScore}</div>
            </div>
            <div className={styles.resultChange}>
              <span className={styles.changePositive}>+{healthImpact.toFixed(1)}</span> points
            </div>
          </div>

          {/* Survival Probability Result */}
          <div className={styles.resultSection}>
            <div className={styles.resultLabel}>Survival Probability</div>
            <div className={styles.resultComparison}>
              <div className={styles.resultBase}>{baseSurvivalProbability}%</div>
              <div className={styles.resultArrow}>→</div>
              <div className={styles.resultProjected}>{updatedSurvivalProbability}%</div>
            </div>
            <div className={styles.resultChange}>
              <span className={styles.changePositive}>+{survivalImpact.toFixed(1)}%</span>
            </div>
          </div>

          {/* Revenue Result */}
          <div className={styles.resultSection}>
            <div className={styles.resultLabel}>Monthly Revenue Forecast</div>
            <div className={styles.resultComparison}>
              <div className={styles.resultBase}>{baseRevenue}M</div>
              <div className={styles.resultArrow}>→</div>
              <div className={styles.resultProjected}>{forecastedRevenue}M</div>
            </div>
            <div className={styles.resultChange}>
              <span className={styles.changePositive}>+{revenueImpact.toFixed(1)}%</span>
            </div>
          </div>

          {/* Impact Breakdown */}
          <div className={styles.breakdownSection}>
            <h3 className={styles.breakdownTitle}>Impact Breakdown</h3>
            <div className={styles.breakdownGrid}>
              <div className={styles.breakdownItem}>
                <div className={styles.breakdownLabel}>Discount Effect</div>
                <div className={styles.breakdownValue}>+{discountImpact.toFixed(1)}%</div>
              </div>
              <div className={styles.breakdownItem}>
                <div className={styles.breakdownLabel}>Cost Savings</div>
                <div className={styles.breakdownValue}>+{costReductionImpact.toFixed(1)}%</div>
              </div>
              <div className={styles.breakdownItem}>
                <div className={styles.breakdownLabel}>Marketing Lift</div>
                <div className={styles.breakdownValue}>+{marketingImpact.toFixed(1)}%</div>
              </div>
              <div className={styles.breakdownItem}>
                <div className={styles.breakdownLabel}>Delivery Integration</div>
                <div className={styles.breakdownValue}>+{deliveryImpact}%</div>
              </div>
            </div>
          </div>

          {/* Reset Button */}
          <button
            className={styles.resetBtn}
            onClick={() => {
              setDiscountPercentage(10);
              setCostReduction(10);
              setMarketingBoost(10);
              setDeliveryIntegration(false);
            }}
          >
            Reset to Defaults
          </button>
        </div>
      </div>
    </div>
  );
}
