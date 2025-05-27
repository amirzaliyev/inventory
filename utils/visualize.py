from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import matplotlib.pyplot as plt
from pandas import DataFrame

from config import MEDIA_DIR


def make_df(
    data: Iterable,
    col_order: Optional[List[str]] = None,
    column_names: Optional[List[str]] = None,
    human_readable: bool = True,
) -> DataFrame:
    df = DataFrame(data)

    if col_order:
        df = df[col_order]

    if column_names:
        df.columns = column_names

    if human_readable is True:
        return df.map(lambda x: f"{x:,}" if isinstance(x, (int, float)) else x)  # type: ignore

    return df  # type: ignore


def to_pdf(title: str, df: DataFrame, period: Dict) -> tuple[str, str]:

    period_str = f"{period['date_from']:%d.%m.%Y} - {period['date_to']:%d.%m.%Y}"

    # Create a figure and an axis
    _, ax = plt.subplots(figsize=(12, 4))
    ax.axis("off")

    # Set title
    ax.set_title(title, fontsize=14, weight="bold", pad=20)
    ax.text(0.7, 1.1, period_str, fontsize=10, weight="semibold")

    # create table
    table = ax.table(
        cellText=df.values, colLabels=df.columns, cellLoc="center", loc="center"  # type: ignore
    )

    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 1.5)

    file_path = Path(MEDIA_DIR, "reports", f"{title} - {period_str}.pdf")
    thumbnail_path = Path(MEDIA_DIR, "thumbnails", f"{title} - {period_str}.png")

    if os.path.exists(file_path):
        os.remove(file_path)

    plt.savefig(file_path, bbox_inches="tight", dpi=200, format="pdf")
    plt.savefig(thumbnail_path, bbox_inches="tight", dpi=200, format="png")

    return str(file_path), str(thumbnail_path)
