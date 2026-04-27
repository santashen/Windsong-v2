-- V8__create_family_portfolio_core_tables.sql
-- Normalized core schema for the family investment portfolio feature.

CREATE OR REPLACE FUNCTION set_updated_at_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TABLE IF NOT EXISTS portfolios (
    id                  BIGSERIAL PRIMARY KEY,
    name                VARCHAR(100) NOT NULL,
    total_principal     NUMERIC(20, 4) NOT NULL DEFAULT 0 CHECK (total_principal >= 0),
    currency            VARCHAR(10) NOT NULL DEFAULT 'CNY',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS assets (
    id                  BIGSERIAL PRIMARY KEY,
    ticker_code         VARCHAR(20) NOT NULL,
    name                VARCHAR(100) NOT NULL,
    sector              VARCHAR(50),
    asset_type          VARCHAR(20) NOT NULL,
    icon_name           VARCHAR(50),
    current_price       NUMERIC(20, 4) CHECK (current_price IS NULL OR current_price >= 0),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_assets_ticker_code UNIQUE (ticker_code),
    CONSTRAINT chk_assets_asset_type
        CHECK (asset_type IN ('stock', 'etf', 'fund', 'bond', 'cash', 'other'))
);

CREATE TABLE IF NOT EXISTS holdings (
    id                  BIGSERIAL PRIMARY KEY,
    portfolio_id        BIGINT NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    asset_id            BIGINT NOT NULL REFERENCES assets(id) ON DELETE RESTRICT,
    invested_amount     NUMERIC(20, 4) NOT NULL DEFAULT 0 CHECK (invested_amount >= 0),
    share_count         NUMERIC(20, 4) NOT NULL DEFAULT 0 CHECK (share_count >= 0),
    average_cost        NUMERIC(20, 4) NOT NULL DEFAULT 0 CHECK (average_cost >= 0),
    weight_percentage   NUMERIC(7, 4) NOT NULL DEFAULT 0 CHECK (weight_percentage >= 0 AND weight_percentage <= 100),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_holdings_portfolio_asset UNIQUE (portfolio_id, asset_id)
);

CREATE TABLE IF NOT EXISTS investment_theses (
    id                          BIGSERIAL PRIMARY KEY,
    asset_id                    BIGINT NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    strategy_tag                VARCHAR(50),
    expected_dividend_yield     NUMERIC(7, 4) CHECK (expected_dividend_yield IS NULL OR expected_dividend_yield >= 0),
    margin_of_safety            NUMERIC(7, 4) CHECK (margin_of_safety IS NULL OR margin_of_safety >= 0),
    valuation_metric_name       VARCHAR(50),
    percentile_value            INTEGER CHECK (percentile_value IS NULL OR (percentile_value >= 0 AND percentile_value <= 100)),
    short_description           VARCHAR(500),
    markdown_details            TEXT,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS performance_history (
    id                  BIGSERIAL PRIMARY KEY,
    portfolio_id        BIGINT NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    record_date         DATE NOT NULL,
    portfolio_nav       NUMERIC(20, 4) NOT NULL CHECK (portfolio_nav >= 0),
    benchmark_nav       NUMERIC(20, 4) CHECK (benchmark_nav IS NULL OR benchmark_nav >= 0),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_performance_history_portfolio_record_date UNIQUE (portfolio_id, record_date)
);

COMMENT ON TABLE portfolios IS 'Top-level family or personal investment portfolio records.';
COMMENT ON TABLE assets IS 'Security master data reused by holdings and thesis records.';
COMMENT ON TABLE holdings IS 'Current portfolio holdings that join a portfolio with an asset.';
COMMENT ON TABLE investment_theses IS 'Qualitative analysis and valuation notes for each asset.';
COMMENT ON TABLE performance_history IS 'Historical daily or periodic NAV data for portfolio vs benchmark.';

CREATE INDEX IF NOT EXISTS idx_assets_asset_type
    ON assets (asset_type);

CREATE INDEX IF NOT EXISTS idx_assets_sector
    ON assets (sector);

CREATE INDEX IF NOT EXISTS idx_holdings_portfolio_id
    ON holdings (portfolio_id);

CREATE INDEX IF NOT EXISTS idx_holdings_asset_id
    ON holdings (asset_id);

CREATE INDEX IF NOT EXISTS idx_investment_theses_asset_id
    ON investment_theses (asset_id);

CREATE INDEX IF NOT EXISTS idx_performance_history_portfolio_date
    ON performance_history (portfolio_id, record_date DESC);

DROP TRIGGER IF EXISTS trg_portfolios_set_updated_at ON portfolios;
CREATE TRIGGER trg_portfolios_set_updated_at
    BEFORE UPDATE ON portfolios
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at_timestamp();

DROP TRIGGER IF EXISTS trg_assets_set_updated_at ON assets;
CREATE TRIGGER trg_assets_set_updated_at
    BEFORE UPDATE ON assets
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at_timestamp();

DROP TRIGGER IF EXISTS trg_holdings_set_updated_at ON holdings;
CREATE TRIGGER trg_holdings_set_updated_at
    BEFORE UPDATE ON holdings
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at_timestamp();

DROP TRIGGER IF EXISTS trg_investment_theses_set_updated_at ON investment_theses;
CREATE TRIGGER trg_investment_theses_set_updated_at
    BEFORE UPDATE ON investment_theses
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at_timestamp();

DROP TRIGGER IF EXISTS trg_performance_history_set_updated_at ON performance_history;
CREATE TRIGGER trg_performance_history_set_updated_at
    BEFORE UPDATE ON performance_history
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at_timestamp();
