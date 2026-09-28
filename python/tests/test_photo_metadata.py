from windsong_python.services.photo_metadata import extract_json


def test_extract_json_accepts_markdown_fence() -> None:
    result = extract_json('```json\n{"items": []}\n```')
    assert result == {"items": []}
