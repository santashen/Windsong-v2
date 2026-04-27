-- Sample local seed data for the family investment portfolio feature.

INSERT INTO portfolios (name, total_principal, currency)
VALUES ('家庭核心配置', 1000000.0000, 'CNY')
ON CONFLICT DO NOTHING;

INSERT INTO assets (ticker_code, name, sector, asset_type, icon_name, current_price) VALUES
('515450.SH', '低波红利50 ETF', '股票指数基金', 'etf', 'shield', 1.1280),
('600941.SH', '中国移动', '电信运营', 'stock', 'cell_tower', 104.1500),
('000333.SZ', '美的集团', '白色家电', 'stock', 'precision_manufacturing', 71.4500)
ON CONFLICT (ticker_code) DO UPDATE
SET
    name = EXCLUDED.name,
    sector = EXCLUDED.sector,
    asset_type = EXCLUDED.asset_type,
    icon_name = EXCLUDED.icon_name,
    current_price = EXCLUDED.current_price;

INSERT INTO investment_theses (asset_id, strategy_tag, expected_dividend_yield, margin_of_safety, markdown_details)
SELECT
    a.id,
    '垄断护城河',
    7.2000,
    35.4000,
    '# 中国移动深度逻辑

### 1. 业务壁垒
拥有全国最大的5G基站覆盖量...

### 2. 现金流分析
资本开支高峰期已过，分红比例持续提升...'
FROM assets a
WHERE a.ticker_code = '600941.SH'
  AND NOT EXISTS (
      SELECT 1
      FROM investment_theses t
      WHERE t.asset_id = a.id
        AND t.strategy_tag = '垄断护城河'
  );
