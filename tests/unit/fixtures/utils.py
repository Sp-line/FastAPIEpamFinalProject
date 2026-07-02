from unittest.mock import MagicMock

import pytest

from app.utils.url import UrlBuilder


@pytest.fixture
def mock_url_builder() -> MagicMock:
    return MagicMock(spec=UrlBuilder)
