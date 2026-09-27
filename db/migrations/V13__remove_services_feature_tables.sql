-- Remove the database objects used by the retired Services pages.
-- Keep this as a forward migration so existing deployments are cleaned up
-- without rewriting Flyway's migration history.

DROP TABLE IF EXISTS family_portfolio_market_sync_logs CASCADE;
DROP TABLE IF EXISTS performance_history CASCADE;
DROP TABLE IF EXISTS investment_theses CASCADE;
DROP TABLE IF EXISTS holdings CASCADE;
DROP TABLE IF EXISTS assets CASCADE;
DROP TABLE IF EXISTS portfolios CASCADE;
DROP TABLE IF EXISTS portfolio_history CASCADE;
DROP TABLE IF EXISTS asset_analysis CASCADE;
DROP TABLE IF EXISTS holding_assets CASCADE;
DROP TABLE IF EXISTS portfolio_snapshots CASCADE;

DROP FUNCTION IF EXISTS set_updated_at_timestamp() CASCADE;
