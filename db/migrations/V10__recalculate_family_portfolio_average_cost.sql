UPDATE holdings
SET average_cost = CASE
    WHEN share_count > 0
    THEN ROUND((invested_amount / share_count)::numeric, 4)
    ELSE 0
END;
