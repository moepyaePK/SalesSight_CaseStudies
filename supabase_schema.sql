-- ============================================
-- SalesSight Database Schema for Supabase
-- ============================================
-- Run this in your Supabase SQL Editor to create all tables

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- Users Table
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(30) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    CONSTRAINT username_length CHECK (char_length(username) >= 3),
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- ============================================
-- Login Attempts Table (for rate limiting)
-- ============================================
CREATE TABLE IF NOT EXISTS login_attempts (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(254) NOT NULL,
    success BOOLEAN DEFAULT FALSE,
    attempted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address VARCHAR(45) -- Optional: store IP for additional security
);

-- Create index for faster rate limit checks
CREATE INDEX IF NOT EXISTS idx_login_attempts_email_time ON login_attempts(email, attempted_at);

-- Auto-delete old login attempts (older than 24 hours)
CREATE OR REPLACE FUNCTION delete_old_login_attempts()
RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM login_attempts 
    WHERE attempted_at < NOW() - INTERVAL '24 hours';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_delete_old_attempts
    AFTER INSERT ON login_attempts
    EXECUTE FUNCTION delete_old_login_attempts();

-- ============================================
-- Feedback Table
-- ============================================
CREATE TABLE IF NOT EXISTS feedback (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_feedback_user ON feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_feedback_created ON feedback(created_at DESC);

-- ============================================
-- Upload History Table
-- ============================================
CREATE TABLE IF NOT EXISTS upload_history (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_size BIGINT NOT NULL,
    row_count INTEGER,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_upload_history_user ON upload_history(user_id);
CREATE INDEX IF NOT EXISTS idx_upload_history_uploaded ON upload_history(uploaded_at DESC);

-- ============================================
-- Forecasts Table (NEW - Feature G)
-- ============================================
CREATE TABLE IF NOT EXISTS forecasts (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    product_name VARCHAR(255),
    forecast_period INTEGER NOT NULL, -- Days forecasted
    forecast_data JSONB NOT NULL, -- Store forecast as JSON array
    actual_data JSONB, -- Store corresponding actual data
    model_used VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_forecasts_user ON forecasts(user_id);
CREATE INDEX IF NOT EXISTS idx_forecasts_created ON forecasts(created_at DESC);

-- ============================================
-- Shared Dashboards Table (NEW - Feature C)
-- ============================================
CREATE TABLE IF NOT EXISTS shared_dashboards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    share_token VARCHAR(255) UNIQUE NOT NULL,
    dashboard_config JSONB NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE,
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_shared_dashboards_owner ON shared_dashboards(owner_id);
CREATE INDEX IF NOT EXISTS idx_shared_dashboards_token ON shared_dashboards(share_token);

-- ============================================
-- Alerts Table (NEW - Feature D)
-- ============================================
CREATE TABLE IF NOT EXISTS alerts (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL, -- 'threshold', 'trend', 'anomaly'
    condition_config JSONB NOT NULL, -- Store alert conditions
    is_active BOOLEAN DEFAULT TRUE,
    last_triggered TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_alerts_user_active ON alerts(user_id, is_active);

-- ============================================
-- Alert History Table
-- ============================================
CREATE TABLE IF NOT EXISTS alert_history (
    id BIGSERIAL PRIMARY KEY,
    alert_id BIGINT REFERENCES alerts(id) ON DELETE CASCADE,
    triggered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    message TEXT NOT NULL,
    data_snapshot JSONB
);

CREATE INDEX IF NOT EXISTS idx_alert_history_alert ON alert_history(alert_id);
CREATE INDEX IF NOT EXISTS idx_alert_history_triggered ON alert_history(triggered_at DESC);

-- ============================================
-- User Preferences Table (NEW - Feature A)
-- ============================================
CREATE TABLE IF NOT EXISTS user_preferences (
    user_id BIGINT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    theme VARCHAR(20) DEFAULT 'light', -- 'light' or 'dark'
    default_forecast_period INTEGER DEFAULT 30,
    email_notifications BOOLEAN DEFAULT TRUE,
    weekly_summary BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- Export History Table (NEW - Feature G)
-- ============================================
CREATE TABLE IF NOT EXISTS export_history (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    export_type VARCHAR(50) NOT NULL, -- 'csv', 'excel', 'pdf'
    filename VARCHAR(255) NOT NULL,
    file_size BIGINT,
    exported_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_export_history_user ON export_history(user_id);

-- ============================================
-- Data Quality Reports Table (NEW - Feature E)
-- ============================================
CREATE TABLE IF NOT EXISTS data_quality_reports (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    upload_id BIGINT REFERENCES upload_history(id) ON DELETE CASCADE,
    missing_values INTEGER,
    duplicate_rows INTEGER,
    anomalies_detected INTEGER,
    quality_score DECIMAL(3,2), -- 0.00 to 1.00
    recommendations JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_quality_reports_upload ON data_quality_reports(upload_id);

-- ============================================
-- Row Level Security (RLS) Policies
-- ============================================
-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE upload_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE forecasts ENABLE ROW LEVEL SECURITY;
ALTER TABLE shared_dashboards ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE export_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE data_quality_reports ENABLE ROW LEVEL SECURITY;

-- Note: Configure RLS policies in Supabase dashboard based on your auth setup
-- Example policy for users table:
-- CREATE POLICY "Users can view own profile" ON users FOR SELECT USING (auth.uid()::bigint = id);

-- ============================================
-- Helpful Views
-- ============================================

-- User activity summary
CREATE OR REPLACE VIEW user_activity_summary AS
SELECT 
    u.id,
    u.username,
    u.email,
    u.created_at,
    u.last_login,
    COUNT(DISTINCT uh.id) as upload_count,
    COUNT(DISTINCT f.id) as forecast_count,
    COUNT(DISTINCT fb.id) as feedback_count,
    AVG(fb.rating) as avg_rating
FROM users u
LEFT JOIN upload_history uh ON u.id = uh.user_id
LEFT JOIN forecasts f ON u.id = f.user_id
LEFT JOIN feedback fb ON u.id = fb.user_id
GROUP BY u.id, u.username, u.email, u.created_at, u.last_login;

-- ============================================
-- Grant Permissions
-- ============================================
-- Note: Adjust these based on your Supabase service role
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO authenticated;
-- GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- ============================================
-- Sample Data (Optional - for testing)
-- ============================================
-- Uncomment to insert sample data

-- INSERT INTO users (username, email, password_hash) VALUES
-- ('demo_user', 'demo@salesight.com', '$2b$12$demo_hash_here');

-- ============================================
-- Database Functions for Common Operations
-- ============================================

-- Function to get user statistics
CREATE OR REPLACE FUNCTION get_user_stats(p_user_id BIGINT)
RETURNS TABLE (
    total_uploads INTEGER,
    total_forecasts INTEGER,
    avg_feedback_rating DECIMAL,
    last_upload_date TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(DISTINCT uh.id)::INTEGER as total_uploads,
        COUNT(DISTINCT f.id)::INTEGER as total_forecasts,
        AVG(fb.rating)::DECIMAL as avg_feedback_rating,
        MAX(uh.uploaded_at) as last_upload_date
    FROM users u
    LEFT JOIN upload_history uh ON u.id = uh.user_id
    LEFT JOIN forecasts f ON u.id = f.user_id
    LEFT JOIN feedback fb ON u.id = fb.user_id
    WHERE u.id = p_user_id
    GROUP BY u.id;
END;
$$ LANGUAGE plpgsql;

-- Function to clean up expired shared dashboards
CREATE OR REPLACE FUNCTION cleanup_expired_dashboards()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM shared_dashboards
    WHERE expires_at IS NOT NULL AND expires_at < NOW();
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Schedule cleanup (run via Supabase Edge Functions or cron job)
-- SELECT cron.schedule('cleanup-dashboards', '0 2 * * *', 'SELECT cleanup_expired_dashboards()');

-- ============================================
-- End of Schema
-- ============================================