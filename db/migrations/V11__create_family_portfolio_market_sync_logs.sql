CREATE TABLE IF NOT EXISTS family_portfolio_market_sync_logs (
    id                      BIGSERIAL PRIMARY KEY,
    run_type                VARCHAR(20) NOT NULL,
    status                  VARCHAR(20) NOT NULL,
    triggered_by            VARCHAR(50),
    asset_update_count      INTEGER NOT NULL DEFAULT 0 CHECK (asset_update_count >= 0),
    asset_success_count     INTEGER NOT NULL DEFAULT 0 CHECK (asset_success_count >= 0),
    portfolio_update_count  INTEGER NOT NULL DEFAULT 0 CHECK (portfolio_update_count >= 0),
    portfolio_success_count INTEGER NOT NULL DEFAULT 0 CHECK (portfolio_success_count >= 0),
    details_json            JSONB,
    error_message           TEXT,
    started_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at             TIMESTAMPTZ,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_family_portfolio_market_sync_logs_started_at
    ON family_portfolio_market_sync_logs (started_at DESC);

DROP TRIGGER IF EXISTS trg_family_portfolio_market_sync_logs_set_updated_at ON family_portfolio_market_sync_logs;
CREATE TRIGGER trg_family_portfolio_market_sync_logs_set_updated_at
BEFORE UPDATE ON family_portfolio_market_sync_logs
FOR EACH ROW
EXECUTE FUNCTION set_updated_at_timestamp();
