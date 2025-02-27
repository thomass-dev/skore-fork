"""SkrubTableReportItem."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .item import ItemTypeError
from .media_item import MediaItem

if TYPE_CHECKING:
    from skrub import TableReport


def factory(table_report: TableReport, /, **kwargs) -> MediaItem:
    """
    Create a new MediaItem instance from a skrub TableReport.

    Parameters
    ----------
    table_report : TableReport
        The report to store.

    Returns
    -------
    MediaItem
        A new MediaItem instance.
    """
    if not hasattr(table_report, "html_snippet"):
        raise ItemTypeError(f"Type '{table_report.__class__}' is not supported.")

    return MediaItem.factory(table_report.html_snippet(), "text/html", **kwargs)
