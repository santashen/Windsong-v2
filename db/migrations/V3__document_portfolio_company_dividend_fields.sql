-- V3__document_portfolio_company_dividend_fields.sql
-- Portfolio company holdings are stored in JSONB. This migration documents
-- the expanded data contract used by the application for dividend analysis.

COMMENT ON COLUMN portfolio_snapshots.holdings IS
'JSONB payload with ETF and company holdings details. Company objects include name, roePct, valuationStatus, shares, eps, payoutRatio, dps, expectedAnnualDividend, averageCost, holdingDividendYieldPct, currentDividendYieldPct.';
