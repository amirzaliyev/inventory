from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Dict, Optional


def get_period(period_title: Optional[str]) -> Dict[str, Any]:
    today = datetime.today().date()

    if period_title == "weekly":
        return {"date_from": today - timedelta(days=7), "date_to": today}

    if period_title == "monthly":
        return {"date_from": today - timedelta(days=30), "date_to": today}

    return {"date_from": date(2000, 1, 1), "date_to": today}
