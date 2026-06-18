from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest

from tests.constants import Markers


def should_run_db(request: pytest.FixtureRequest) -> bool:
    config = request.config
    mark_option = config.getoption("-m", "")

    if Markers.REQUIRES_DB in mark_option:
        return True

    if f"not {Markers.REQUIRES_DB}" in mark_option:
        return False

    return any(
        bool(item.get_closest_marker(Markers.REQUIRES_DB))
        for item in request.session.items
    )
