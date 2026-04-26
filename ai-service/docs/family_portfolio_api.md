# Family Portfolio API

Base path: `/api/family-portfolio`

## Endpoints

### `GET /portfolios`
- Purpose: list all portfolios.
- Service: `FamilyPortfolioService.list_portfolios`
- Response:
```json
{
  "items": [
    {
      "id": 1,
      "name": "家庭核心配置",
      "total_principal": "1000000.0000",
      "currency": "CNY",
      "created_at": "2026-04-26T13:47:28.156376Z",
      "updated_at": "2026-04-26T13:47:28.156376Z"
    }
  ]
}
```

### `POST /portfolios`
- Purpose: create one portfolio.
- Service: `FamilyPortfolioService.create_portfolio`
- Request:
```json
{
  "name": "家庭核心配置",
  "total_principal": "1000000.0000",
  "currency": "CNY"
}
```

### `PUT /portfolios/{portfolio_id}`
- Purpose: update one portfolio by id.
- Service: `FamilyPortfolioService.update_portfolio`

### `DELETE /portfolios/{portfolio_id}`
- Purpose: delete one portfolio by id.
- Service: `FamilyPortfolioService.delete_portfolio`

### `GET /portfolios/{portfolio_id}`
- Purpose: return one portfolio with holdings, latest thesis per asset, and performance history.
- Service: `FamilyPortfolioService.get_portfolio_detail`

### `GET /assets`
- Purpose: list all assets.
- Service: `FamilyPortfolioService.list_assets`

### `POST /assets`
- Purpose: create or upsert one asset by `ticker_code`.
- Service: `FamilyPortfolioService.create_asset`
- Request:
```json
{
  "ticker_code": "600941.SH",
  "name": "中国移动",
  "sector": "电信运营",
  "asset_type": "stock",
  "icon_name": "cell_tower",
  "current_price": "104.1500"
}
```

### `PUT /assets/{asset_id}`
- Purpose: update one asset by id.
- Service: `FamilyPortfolioService.update_asset`

### `DELETE /assets/{asset_id}`
- Purpose: delete one asset by id.
- Service: `FamilyPortfolioService.delete_asset`

### `POST /holdings`
- Purpose: create or upsert one holding by `(portfolio_id, asset_id)`.
- Service: `FamilyPortfolioService.create_holding`

### `PUT /holdings/{holding_id}`
- Purpose: update one holding by id.
- Service: `FamilyPortfolioService.update_holding`

### `DELETE /holdings/{holding_id}`
- Purpose: delete one holding by id.
- Service: `FamilyPortfolioService.delete_holding`

### `POST /investment-theses`
- Purpose: create one thesis row for an asset.
- Service: `FamilyPortfolioService.create_investment_thesis`

### `PUT /investment-theses/{thesis_id}`
- Purpose: update one thesis by id.
- Service: `FamilyPortfolioService.update_investment_thesis`

### `DELETE /investment-theses/{thesis_id}`
- Purpose: delete one thesis by id.
- Service: `FamilyPortfolioService.delete_investment_thesis`

### `POST /performance-history`
- Purpose: create or upsert one NAV record by `(portfolio_id, record_date)`.
- Service: `FamilyPortfolioService.create_performance_history`

### `PUT /performance-history/{history_id}`
- Purpose: update one NAV record by id.
- Service: `FamilyPortfolioService.update_performance_history`

### `DELETE /performance-history/{history_id}`
- Purpose: delete one NAV record by id.
- Service: `FamilyPortfolioService.delete_performance_history`

## Notes

- `asset_type` must be one of `stock`, `etf`, `fund`, `bond`, `cash`, `other`.
- Monetary and ratio fields are stored as PostgreSQL `NUMERIC`, so API responses keep decimal values as strings.
- Portfolio detail currently returns the latest thesis per asset, ordered by `updated_at DESC, id DESC`.
- All write operations (`POST`, `PUT`, `DELETE`) require admin auth through `X-API-Key: <ADMIN_API_KEY>` or `Authorization: Bearer <ADMIN_API_KEY>`.
- If `ADMIN_API_KEY` is empty, write auth is skipped to match the existing backend development behavior.
