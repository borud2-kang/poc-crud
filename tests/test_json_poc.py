"""
json_poc.py Regression / Safety 테스트

- 정상 케이스(직렬화/역직렬화/파일 입출력)가 계속 동작하는지 (Regression)
- 비정상 입력(잘못된 JSON, 지원 안 되는 타입)에서 앱이 죽지 않고 예상된 예외로
  안전하게 실패하는지 (Safety)
를 함께 검증한다.
"""

import json
import os
from datetime import datetime

import pytest

import json_poc


def test_dumps_loads_roundtrip_preserves_data():
    json_str = json.dumps(json_poc.SAMPLE_DATA, ensure_ascii=False)
    restored = json.loads(json_str)
    assert restored == json_poc.SAMPLE_DATA


def test_dump_load_file_roundtrip(tmp_path):
    file_path = tmp_path / "sample.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(json_poc.SAMPLE_DATA, f, ensure_ascii=False, indent=2)

    with open(file_path, "r", encoding="utf-8") as f:
        loaded = json.load(f)

    assert loaded == json_poc.SAMPLE_DATA


def test_ensure_ascii_false_keeps_korean_readable():
    json_str = json.dumps({"name": "홍길동"}, ensure_ascii=False)
    assert "홍길동" in json_str
    assert "\\u" not in json_str


@pytest.mark.parametrize(
    "broken_json",
    [
        '{"name": "홍길동", "age": }',  # 값 누락
        '{"name": "홍길동" "age": 10}',  # 콤마 누락
        '{"name": "홍길동",}',  # trailing comma
        "",  # 빈 문자열
        "not even json",
    ],
)
def test_invalid_json_raises_decode_error_safely(broken_json):
    with pytest.raises(json.JSONDecodeError):
        json.loads(broken_json)


def test_datetime_not_serializable_without_default_callback():
    with pytest.raises(TypeError):
        json.dumps({"created_at": datetime(2026, 1, 1)})


def test_datetime_serializable_with_default_callback():
    def default_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    result = json.dumps(
        {"created_at": datetime(2026, 1, 1, 10, 30)},
        default=default_serializer,
        ensure_ascii=False,
    )
    assert result == '{"created_at": "2026-01-01T10:30:00"}'


def test_full_script_runs_end_to_end_without_error(tmp_path, monkeypatch):
    """json_poc.main() 전체 흐름이 예외 없이 끝까지 실행되고, 임시 파일도 정리되는지 확인."""
    temp_file = tmp_path / "sample.json"
    monkeypatch.setattr(json_poc, "DATA_FILE", str(temp_file))

    json_poc.main()

    assert not os.path.exists(temp_file)
