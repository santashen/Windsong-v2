WITH portfolio_totals AS (
    SELECT portfolio_id, COALESCE(SUM(invested_amount), 0) AS total_principal
    FROM holdings
    GROUP BY portfolio_id
)
UPDATE holdings h
SET weight_percentage = CASE
    WHEN portfolio_totals.total_principal > 0
    THEN ROUND((h.invested_amount / portfolio_totals.total_principal * 100)::numeric, 4)
    ELSE 0
END
FROM portfolio_totals
WHERE h.portfolio_id = portfolio_totals.portfolio_id;

UPDATE portfolios p
SET total_principal = COALESCE((
    SELECT SUM(h.invested_amount)
    FROM holdings h
    WHERE h.portfolio_id = p.id
), 0);
