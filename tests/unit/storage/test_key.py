from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from app.schemas.storage import DocumentKeyBuild
from app.schemas.storage import KeyBuild
from app.storage.key import DocumentKeyStrategy
from app.storage.key import S3KeyStrategy


class DummyKeyStrategy(S3KeyStrategy[KeyBuild]):
    def generate(self, _data: KeyBuild) -> str:
        return f"{self._prefix}/dummy"


def test_s3_key_strategy_initializes_prefix_in_concrete_class() -> None:
    strategy = DummyKeyStrategy("test_prefix")

    assert strategy._prefix == "test_prefix"  # noqa: SLF001


def test_document_key_strategy_initializes_with_correct_prefix(
    document_key_strategy: DocumentKeyStrategy,
) -> None:
    assert document_key_strategy._prefix == "documents"  # noqa: SLF001


@pytest.mark.parametrize(
    ("original_name", "expected_slug"),
    [
        ("Simple Name.pdf", "simple_name_pdf"),
        ("Name With  Spaces", "name_with_spaces"),
        ("Special!@#Chars.doc", "special_chars_doc"),
        (
            "Very Long Name That Exceeds Fifty Characters Limit Easily.txt",
            "very_long_name_that_exceeds_fifty_characters_limit",
        ),
        ("Кирилиця Тест.png", "kirilitsia_test_png"),
    ],
    ids=[
        "simple_name",
        "multiple_spaces",
        "special_characters",
        "truncated_at_50_chars",
        "cyrillic_transliteration",
    ],
)
@patch("app.storage.key.uuid4")
def test_document_key_strategy_generates_correct_key(
    mock_uuid4: MagicMock,
    document_key_strategy: DocumentKeyStrategy,
    original_name: str,
    expected_slug: str,
) -> None:
    mock_uuid = "12345678-1234-1234-1234-1234567890ab"
    mock_uuid4.return_value = mock_uuid
    build_data = DocumentKeyBuild(project_id=42, original_name=original_name)

    result = document_key_strategy.generate(build_data)

    expected_key = f"documents/42/{expected_slug}_{mock_uuid}"
    assert result == expected_key
