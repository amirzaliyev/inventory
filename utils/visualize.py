from __future__ import annotations

import os
from decimal import Decimal
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import matplotlib.pyplot as plt
from pandas import DataFrame

from config import MEDIA_DIR


def make_df(
    data: Iterable,
    col_order: Optional[List[str]] = None,
    column_names: Optional[List[str]] = None,
    sort_by: Optional[str] = None,
) -> DataFrame:
    df = DataFrame(data)

    if col_order:
        df = df[col_order]

    if column_names:
        df.columns = column_names

    if sort_by:
        df.sort_values(by=sort_by, ascending=False, inplace=True)

    return df  # type: ignore


def make_human_readable(df):
    return df.map(lambda x: f"{x:,}" if isinstance(x, (int, float, Decimal)) else x)  # type: ignore


def to_pdf(
    title: str, df: DataFrame, period: Dict, figsize: Optional[tuple[int, int]] = None
) -> tuple[str, str]:

    period_str = f"{period['date_from']:%d.%m.%Y} - {period['date_to']:%d.%m.%Y}"

    # Create a figure and an axis
    if figsize is None:
        figsize = (8, 2)

    _, ax = plt.subplots(figsize=figsize)
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

    if os.path.exists(thumbnail_path):
        os.remove(thumbnail_path)

    plt.savefig(file_path, bbox_inches="tight", dpi=200, format="pdf")
    plt.savefig(thumbnail_path, bbox_inches="tight", dpi=100, format="png")

    return str(file_path), str(thumbnail_path)
