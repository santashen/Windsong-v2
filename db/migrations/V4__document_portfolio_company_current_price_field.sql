-- V4__document_portfolio_company_current_price_field.sql
-- Update the documented JSONB contract for company holdings to use currentPrice.

COMMENT ON COLUMN portfolio_snapshots.holdings IS
'JSONB payload with ETF and company holdings details. Company objects include name, valuationStatus, shares, eps, payoutRatio, dps, expectedAnnualDividend, averageCost, currentPrice, holdingDividendYieldPct, currentDividendYieldPct.';
