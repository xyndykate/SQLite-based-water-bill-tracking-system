-- SQLite Database Schema for Water Bill Tracking System
-- SQLite-specific features and syntax

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Create tenants table
CREATE TABLE IF NOT EXISTS tenants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    apartment_number TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

-- Create water_readings table
CREATE TABLE IF NOT EXISTS water_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL,
    reading_units REAL NOT NULL,
    reading_date DATETIME NOT NULL,
    recorded_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    created_by TEXT,
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id) ON DELETE CASCADE
);

-- Create bills table
CREATE TABLE IF NOT EXISTS bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL,
    bill_period_start DATE NOT NULL,
    bill_period_end DATE NOT NULL,
    start_reading_id INTEGER,
    end_reading_id INTEGER,
    units_consumed REAL NOT NULL,
    rate_per_unit REAL NOT NULL,
    total_amount REAL NOT NULL,
    currency TEXT DEFAULT 'USD',
    bill_status TEXT DEFAULT 'generated',
    generated_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    due_date DATE,
    paid_date DATETIME,
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    FOREIGN KEY (start_reading_id) REFERENCES water_readings(id),
    FOREIGN KEY (end_reading_id) REFERENCES water_readings(id)
);

-- Create settings table for system configuration
CREATE TABLE IF NOT EXISTS system_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_key TEXT UNIQUE NOT NULL,
    setting_value TEXT NOT NULL,
    description TEXT,
    updated_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insert default settings
INSERT OR IGNORE INTO system_settings (setting_key, setting_value, description) VALUES
    ('default_rate_per_unit', '2.50', 'Default rate per water unit'),
    ('default_currency', 'USD', 'Default currency for bills'),
    ('billing_cycle_days', '30', 'Default billing cycle in days'),
    ('late_fee_percentage', '5.0', 'Late fee percentage'),
    ('grace_period_days', '10', 'Grace period before late fees apply');

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_water_readings_tenant_id ON water_readings(tenant_id);
CREATE INDEX IF NOT EXISTS idx_water_readings_date ON water_readings(reading_date);
CREATE INDEX IF NOT EXISTS idx_bills_tenant_id ON bills(tenant_id);
CREATE INDEX IF NOT EXISTS idx_bills_period ON bills(bill_period_start, bill_period_end);
CREATE INDEX IF NOT EXISTS idx_tenants_apartment ON tenants(apartment_number);

-- Create trigger to update the updated_date field for tenants
CREATE TRIGGER IF NOT EXISTS update_tenants_updated_date 
    AFTER UPDATE ON tenants
    FOR EACH ROW
BEGIN
    UPDATE tenants SET updated_date = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Create trigger to update the updated_date field for settings
CREATE TRIGGER IF NOT EXISTS update_settings_updated_date 
    AFTER UPDATE ON system_settings
    FOR EACH ROW
BEGIN
    UPDATE system_settings SET updated_date = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Create view for tenant summary
CREATE VIEW IF NOT EXISTS tenant_summary AS
SELECT 
    t.tenant_id,
    t.name,
    t.apartment_number,
    t.phone,
    t.email,
    t.created_date,
    COUNT(wr.id) as total_readings,
    MAX(wr.reading_date) as last_reading_date,
    COUNT(b.id) as total_bills,
    COALESCE(SUM(CASE WHEN b.bill_status = 'paid' THEN b.total_amount ELSE 0 END), 0) as total_paid,
    COALESCE(SUM(CASE WHEN b.bill_status != 'paid' THEN b.total_amount ELSE 0 END), 0) as outstanding_amount
FROM tenants t
LEFT JOIN water_readings wr ON t.tenant_id = wr.tenant_id
LEFT JOIN bills b ON t.tenant_id = b.tenant_id
WHERE t.is_active = 1
GROUP BY t.tenant_id, t.name, t.apartment_number, t.phone, t.email, t.created_date;

-- Create view for monthly consumption reports
CREATE VIEW IF NOT EXISTS monthly_consumption AS
SELECT 
    DATE(wr.reading_date, 'start of month') as month,
    t.tenant_id,
    t.name,
    t.apartment_number,
    COUNT(wr.id) as readings_count,
    MIN(wr.reading_units) as month_start_reading,
    MAX(wr.reading_units) as month_end_reading,
    MAX(wr.reading_units) - MIN(wr.reading_units) as consumption
FROM tenants t
JOIN water_readings wr ON t.tenant_id = wr.tenant_id
WHERE t.is_active = 1
GROUP BY DATE(wr.reading_date, 'start of month'), t.tenant_id, t.name, t.apartment_number
HAVING COUNT(wr.id) >= 2
ORDER BY month DESC, t.apartment_number;