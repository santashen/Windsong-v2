-- V2__create_portfolio_snapshots_table.sql
-- Historical snapshots for the family investment portfolio.
-- The public-facing page will always read the latest snapshot,
-- while admin can append a new snapshot without overwriting history.

CREATE TABLE IF NOT EXISTS portfolio_snapshots (
    id                              BIGSERIAL PRIMARY KEY,
    record_date                     DATE NOT NULL,
    total_principal                 NUMERIC(18, 2) NOT NULL CHECK (total_principal >= 0),
    total_market_value              NUMERIC(18, 2) NOT NULL CHECK (total_market_value >= 0),
    expected_annual_dividends       NUMERIC(18, 2) NOT NULL CHECK (expected_annual_dividends >= 0),
    portfolio_dividend_yield_pct    NUMERIC(8, 4) NOT NULL CHECK (portfolio_dividend_yield_pct >= 0),
    market_value_dividend_yield_pct NUMERIC(8, 4) NOT NULL CHECK (market_value_dividend_yield_pct >= 0),
    manager_comment                 TEXT,
    holdings                        JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at                      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE portfolio_snapshots IS 'Historical family portfolio snapshots. Each insert represents one reporting period.';
COMMENT ON COLUMN portfolio_snapshots.record_date IS 'Reporting date shown to family members.';
COMMENT ON COLUMN portfolio_snapshots.holdings IS 'JSONB payload with ETF and company holdings details for the snapshot.';

CREATE INDEX IF NOT EXISTS idx_portfolio_snapshots_record_date
    ON portfolio_snapshots (record_date DESC);

CREATE INDEX IF NOT EXISTS idx_portfolio_snapshots_created_at
    ON portfolio_snapshots (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_portfolio_snapshots_holdings_gin
    ON portfolio_snapshots
    USING GIN (holdings);
