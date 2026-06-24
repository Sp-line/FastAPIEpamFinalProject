import pytest

from app.utils.case_converter import camel_case_to_snake_case


@pytest.mark.parametrize(
    ("input_string", "expected_result"),
    [
        ("PascalCaseString", "pascal_case_string"),
        ("camelCaseString", "camel_case_string"),
        ("HTTPResponseCode", "http_response_code"),
        ("getURL", "get_url"),
        ("user123Id", "user123_id"),
        ("", ""),
        ("A", "a"),
        ("already_snake_case", "already_snake_case"),
    ],
    ids=[
        "standard_pascal_case",
        "standard_camel_case",
        "acronym_in_the_middle",
        "acronym_at_the_end",
        "numbers_handled_correctly",
        "empty_string",
        "single_upper_char",
        "already_snake_case_unchanged",
    ],
)
def test_camel_case_to_snake_case_converts_correctly(
    input_string: str,
    expected_result: str,
) -> None:
    result = camel_case_to_snake_case(input_string)

    assert result == expected_result
