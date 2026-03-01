-- PayLabs Merchant Health Database Initialization
-- Creates tables for transactions, health snapshots, and AI recommendations

USE paylabs_merchant;

-- Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id VARCHAR(64) UNIQUE NOT NULL,
    merchant_id VARCHAR(32) NOT NULL INDEX,
    amount DECIMAL(15, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'IDR',
    payment_method VARCHAR(32),
    transaction_type VARCHAR(32),
    status VARCHAR(32) INDEX,
    is_anomaly BOOLEAN DEFAULT FALSE,
    anomaly_score DECIMAL(5, 4),
    transaction_time DATETIME INDEX,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    raw_data JSON,
    INDEX idx_merchant_time (merchant_id, transaction_time),
    INDEX idx_status_time (status, transaction_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Merchant health snapshots table
CREATE TABLE IF NOT EXISTS merchant_health_snapshots (
    id INT AUTO_INCREMENT PRIMARY KEY,
    merchant_id VARCHAR(32) NOT NULL INDEX,
    snapshot_date DATETIME NOT NULL,
    health_score DECIMAL(5, 2) NOT NULL,
    survival_probability DECIMAL(5, 2) NOT NULL,
    risk_level VARCHAR(16),
    daily_revenue DECIMAL(15, 2),
    revenue_change DECIMAL(8, 4),
    volatility_score DECIMAL(5, 2),
    cashflow_stress_index DECIMAL(5, 2),
    peer_percentile DECIMAL(5, 2),
    repeat_ratio DECIMAL(4, 2),
    ai_insights JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_merchant_date (merchant_id, snapshot_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- AI recommendations table
CREATE TABLE IF NOT EXISTS ai_recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    merchant_id VARCHAR(32) NOT NULL INDEX,
    recommendation_type VARCHAR(32),
    title VARCHAR(256) NOT NULL,
    description TEXT,
    severity VARCHAR(16),
    priority VARCHAR(16),
    expected_revenue_impact DECIMAL(6, 2),
    expected_health_impact DECIMAL(6, 2),
    status VARCHAR(16) DEFAULT 'pending',
    implemented_at DATETIME,
    model_used VARCHAR(64),
    confidence_score DECIMAL(4, 3),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP INDEX,
    INDEX idx_merchant_status (merchant_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Simulation results table
CREATE TABLE IF NOT EXISTS simulation_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    merchant_id VARCHAR(32) NOT NULL INDEX,
    discount_percentage DECIMAL(5, 2) DEFAULT 0,
    cost_reduction_percentage DECIMAL(5, 2) DEFAULT 0,
    marketing_boost_percentage DECIMAL(5, 2) DEFAULT 0,
    delivery_integration BOOLEAN DEFAULT FALSE,
    forecasted_revenue DECIMAL(15, 2),
    updated_health_score DECIMAL(5, 2),
    updated_survival_probability DECIMAL(5, 2),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert sample data for testing (optional)
-- Uncomment to add sample transactions
/*
INSERT INTO transactions (transaction_id, merchant_id, amount, currency, payment_method, status, transaction_time) VALUES
('TXN001', 'MERCHANT001', 150000, 'IDR', 'qris', 'success', NOW() - INTERVAL 1 DAY),
('TXN002', 'MERCHANT001', 275000, 'IDR', 'va', 'success', NOW() - INTERVAL 2 DAY),
('TXN003', 'MERCHANT001', 89000, 'IDR', 'qris', 'success', NOW() - INTERVAL 3 DAY),
('TXN004', 'MERCHANT001', 450000, 'IDR', 'cc', 'success', NOW() - INTERVAL 4 DAY),
('TXN005', 'MERCHANT001', 125000, 'IDR', 'emoney', 'success', NOW() - INTERVAL 5 DAY);
*/
