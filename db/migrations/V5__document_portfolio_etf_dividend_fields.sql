-- V5__document_portfolio_etf_dividend_fields.sql
-- Update the documented JSONB contract for ETF holdings to include ownership and dividend fields.

COMMENT ON COLUMN portfolio_snapshots.holdings IS
'JSONB payload with ETF and company holdings details. ETF objects include name, weightPct, shares, averageCost, dividendPerShare, expectedAnnualDividend, yieldOnCost, currentReferencePrice. Company objects include name, valuationStatus, shares, eps, payoutRatio, dps, expectedAnnualDividend, averageCost, currentPrice, holdingDividendYieldPct, currentDividendYieldPct.';
