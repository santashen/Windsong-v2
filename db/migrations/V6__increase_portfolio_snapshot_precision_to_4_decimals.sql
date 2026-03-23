-- V6__increase_portfolio_snapshot_precision_to_4_decimals.sql
-- Increase portfolio snapshot monetary precision from 2 decimal places to 4.

ALTER TABLE portfolio_snapshots
    ALTER COLUMN total_principal TYPE NUMERIC(18, 4),
    ALTER COLUMN total_market_value TYPE NUMERIC(18, 4),
    ALTER COLUMN expected_annual_dividends TYPE NUMERIC(18, 4);
