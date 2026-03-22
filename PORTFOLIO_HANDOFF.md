# Portfolio Handoff

This file is a compact handoff for continuing the family portfolio feature work in a new Codex conversation.

## Goal

Build and refine a family portfolio system for a value-investing presentation flow:

- Public-facing page is for family members.
- It always reads and shows only the latest portfolio snapshot.
- It avoids stock-app style noise such as flashing gains/losses or intraday charts.
- It emphasizes ownership of businesses, dividend cash flow, valuation discipline, and long-term calm presentation.

## Current Architecture

### Database

- PostgreSQL
- Flyway migrations in `db/migrations`
- Portfolio snapshots are stored in a single historical table:
  - `portfolio_snapshots`
  - one row per reporting period
  - holdings are stored as `JSONB`

### Backend

- Go + Gin + GORM
- Public family portfolio access is password-protected with `PORTFOLIO_ACCESS_PASSWORD`
- Admin creation uses the existing admin API key flow

### Frontend

- Vue 3 + Vite
- Public page route: `/portfolio`
- Admin page route: `/admin/portfolio`

## Relevant Files

### Migrations

- `db/migrations/V2__create_portfolio_snapshots_table.sql`
- `db/migrations/V3__document_portfolio_company_dividend_fields.sql`
- `db/migrations/V4__document_portfolio_company_current_price_field.sql`

### Backend

- `backend/models/portfolio.go`
- `backend/handlers/portfolio.go`
- `backend/services/portfolio.go`
- `backend/middleware/portfolio_auth.go`
- `backend/routes/routes.go`
- `backend/config/config.go`

### Frontend

- `frontend/src/views/PortfolioView.vue`
- `frontend/src/views/admin/Portfolio.vue`
- `frontend/src/api/portfolio.js`
- `frontend/src/router/index.js`
- `frontend/src/components/layout/Header.vue`
- `frontend/src/components/admin/AdminSidebar.vue`

### Env / Deploy

- `.env.prod.example`
- `backend/.env.example`
- `docker-compose.prod.yml`
- `.github/workflows/deploy.yml`

## Current Data Shape

### Snapshot overview

- `recordDate`
- `totalPrincipal`
- `totalMarketValue`
- `expectedAnnualDividends`
- `portfolioDividendYieldPct`
- `marketValueDividendYieldPct`
- `managerComment`
- `holdings`

### ETF holding

- `name`
- `weightPct`
- `averageCost`
- `currentReferencePrice`

### Company holding

- `name`
- `valuationStatus`
- `shares`
- `eps`
- `payoutRatio`
- `dps`
- `expectedAnnualDividend`
- `averageCost`
- `currentPrice`
- `holdingDividendYieldPct`
- `currentDividendYieldPct`

## Current UI Decisions

### Public page

`frontend/src/views/PortfolioView.vue`

- Uses site `Header` and `Footer`
- Public route is aligned to the rest of the site visually
- Login/auth card is integrated into the page, not a separate app-like screen
- “Excellent companies” cards are split into 3 layers:
  - top: company name + valuation tag
  - layer 1: business capability
    - `EPS`
    - `payoutRatio`
    - `dps`
  - layer 2: ownership emphasis
    - `shares`
    - `expectedAnnualDividend`
  - layer 3: quality and cost
    - left column intent: `averageCost`, `holdingDividendYieldPct`
    - right column intent: `currentPrice`, `currentDividendYieldPct`

### Admin page

`frontend/src/views/admin/Portfolio.vue`

- Admin can append a new snapshot
- Company form currently computes:
  - `dps = eps * payoutRatio / 100`
  - `expectedAnnualDividend = shares * dps`
- These computed values are sent in payload

## API Endpoints

### Public

- `POST /api/v1/portfolio/access/verify`
- `GET /api/v1/portfolio/latest`
  - requires header: `X-Portfolio-Password`

### Admin

- `POST /api/v1/portfolio/snapshots`
  - requires header: `X-API-Key`

## Environment Variables

### Important

- `PORTFOLIO_ACCESS_PASSWORD`
- `ADMIN_API_KEY`
- `DATABASE_URL`

## Verified State

At the time of writing:

- `npm run build` passes
- `go build ./...` passes

## Recent Commit Sequence

Useful recent commits on `feat/portfolio`:

- `f328b45` feat: add portfolio snapshot schema and deploy config
- `6ddd829` feat: add family portfolio management flow
- `abd6f1d` style: align portfolio page with site layout
- `bca82dc` style: refine portfolio page visual language
- `2c70f0b` feat: enrich portfolio company dividend model

## Known Next-Step Areas

These are reasonable follow-up refactors:

1. Refine the “excellent companies” card layout further so the lower metrics area reads as a strict 2-column comparison:
   - left: average cost / holding dividend yield
   - right: current price / current dividend yield

2. Improve admin UX for company entry:
   - clearer formula guidance
   - maybe auto-calculate current dividend yield from `dps / currentPrice`
   - maybe auto-calculate holding dividend yield from `dps / averageCost`

3. Consider adding snapshot preview in admin before submit.

4. Consider adding explicit TypeScript-style shared schema documentation for frontend/backend payload consistency, even if code remains JS/Go.

5. Consider whether old snapshots without new company fields need compatibility handling in UI.

## Notes for the Next Codex

- Do not introduce stock-app style gain/loss flashing or red/green intraday UI.
- Keep the tone calm, long-term, white-background, research-like.
- Preserve the “family explanation” intent rather than turning it into a trading dashboard.
- The table data is historical and append-only; do not overwrite old snapshots.
