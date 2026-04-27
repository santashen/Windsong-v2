from __future__ import annotations

import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database import get_db_connection


HISTORY_POINTS: list[tuple[date, Decimal, Decimal]] = [
    (date(2025, 1, 31), Decimal("1.0000"), Decimal("1.0000")),
    (date(2025, 2, 28), Decimal("1.0185"), Decimal("1.0112")),
    (date(2025, 3, 31), Decimal("1.0321"), Decimal("1.0068")),
    (date(2025, 4, 30), Decimal("1.0214"), Decimal("0.9885")),
    (date(2025, 5, 31), Decimal("1.0478"), Decimal("1.0024")),
    (date(2025, 6, 30), Decimal("1.0836"), Decimal("1.0249")),
    (date(2025, 7, 31), Decimal("1.1092"), Decimal("1.0396")),
    (date(2025, 8, 31), Decimal("1.0947"), Decimal("1.0128")),
    (date(2025, 9, 30), Decimal("1.1265"), Decimal("1.0281")),
    (date(2025, 10, 31), Decimal("1.1589"), Decimal("1.0435")),
    (date(2025, 11, 30), Decimal("1.1734"), Decimal("1.0518")),
    (date(2025, 12, 31), Decimal("1.1896"), Decimal("1.0632")),
    (date(2026, 1, 31), Decimal("1.2148"), Decimal("1.0749")),
    (date(2026, 2, 28), Decimal("1.2382"), Decimal("1.0864")),
    (date(2026, 3, 31), Decimal("1.2271"), Decimal("1.0716")),
    (date(2026, 4, 26), Decimal("1.2539"), Decimal("1.0958")),
]


def resolve_target_portfolio() -> tuple[int, str]:
    query = """
        SELECT id, name
        FROM portfolios
        WHERE name = '家庭核心配置'
        ORDER BY id DESC
        LIMIT 1
    """
    fallback_query = """
        SELECT id, name
        FROM portfolios
        ORDER BY id DESC
        LIMIT 1
    """
    with get_db_connection() as connection, connection.cursor() as cursor:
        cursor.execute(query)
        row = cursor.fetchone()
        if row:
            return int(row["id"]), str(row["name"])
        cursor.execute(fallback_query)
        row = cursor.fetchone()
        if row:
            return int(row["id"]), str(row["name"])
    raise RuntimeError("No portfolio found. Create a portfolio before seeding history.")


def seed_history(portfolio_id: int) -> int:
    upsert_query = """
        INSERT INTO performance_history (
            portfolio_id,
            record_date,
            portfolio_nav,
            benchmark_nav
        )
        VALUES (
            %(portfolio_id)s,
            %(record_date)s,
            %(portfolio_nav)s,
            %(benchmark_nav)s
        )
        ON CONFLICT (portfolio_id, record_date) DO UPDATE
        SET
            portfolio_nav = EXCLUDED.portfolio_nav,
            benchmark_nav = EXCLUDED.benchmark_nav
    """
    with get_db_connection() as connection, connection.cursor() as cursor:
        for record_date, portfolio_nav, benchmark_nav in HISTORY_POINTS:
            cursor.execute(
                upsert_query,
                {
                    "portfolio_id": portfolio_id,
                    "record_date": record_date,
                    "portfolio_nav": portfolio_nav,
                    "benchmark_nav": benchmark_nav,
                },
            )
    return len(HISTORY_POINTS)


def main() -> None:
    portfolio_id, portfolio_name = resolve_target_portfolio()
    seeded_count = seed_history(portfolio_id)
    print(
        f"Seeded {seeded_count} performance history rows into portfolio "
        f"{portfolio_id} ({portfolio_name})."
    )


if __name__ == "__main__":
    main()
