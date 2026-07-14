"""
JSON 파싱 / 저장 PoC (Proof of Concept)
표준 라이브러리 `json` 모듈만 사용해서 다음을 검증한다.
  1. dict/list  ->  JSON 문자열 (직렬화, dumps)
  2. JSON 문자열 -> dict/list  (역직렬화, loads)
  3. dict/list  ->  JSON 파일 저장 (dump)
  4. JSON 파일  ->  dict/list  읽기 (load)
  5. 파싱 실패(잘못된 JSON) 처리
  6. 커스텀 객체 직렬화 (datetime 등 기본으로 안 되는 타입)
"""

import json
import os
from datetime import datetime

SAMPLE_DATA = {
    "id": 1,
    "name": "홍길동",
    "active": True,
    "score": 87.5,
    "tags": ["python", "poc", "json"],
    "address": {
        "city": "서울",
        "zipcode": "04524",
    },
    "children": None,
}

DATA_FILE = os.path.join(os.path.dirname(__file__), "sample.json")


def step1_dumps():
    print("=== 1. dict -> JSON 문자열 (dumps) ===")
    json_str = json.dumps(SAMPLE_DATA, ensure_ascii=False, indent=2)
    print(json_str)
    return json_str


def step2_loads(json_str):
    print("\n=== 2. JSON 문자열 -> dict (loads) ===")
    parsed = json.loads(json_str)
    print(type(parsed), parsed["name"], parsed["address"]["city"])
    return parsed


def step3_dump_to_file(data):
    print(f"\n=== 3. dict -> JSON 파일 저장 (dump): {DATA_FILE} ===")
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("저장 완료")


def step4_load_from_file():
    print(f"\n=== 4. JSON 파일 -> dict 읽기 (load): {DATA_FILE} ===")
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    print(loaded)
    return loaded


def step5_invalid_json():
    print("\n=== 5. 잘못된 JSON 파싱 시 에러 처리 ===")
    broken_json = '{"name": "홍길동", "age": }'  # 값 누락 -> 문법 오류
    try:
        json.loads(broken_json)
    except json.JSONDecodeError as e:
        print(f"파싱 실패 (예상된 동작): {e}")


def step6_custom_type():
    print("\n=== 6. datetime 등 기본 미지원 타입 직렬화 ===")

    def default_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    data_with_datetime = {"created_at": datetime(2026, 7, 14, 10, 30)}

    # 기본 dumps는 datetime을 처리 못해 TypeError 발생
    try:
        json.dumps(data_with_datetime)
    except TypeError as e:
        print(f"기본 방식 실패 (예상된 동작): {e}")

    # default 콜백을 넘기면 처리 가능
    result = json.dumps(data_with_datetime, default=default_serializer, ensure_ascii=False)
    print(f"default= 콜백 사용 시 성공: {result}")


def main():
    json_str = step1_dumps()
    step2_loads(json_str)
    step3_dump_to_file(SAMPLE_DATA)
    step4_load_from_file()
    step5_invalid_json()
    step6_custom_type()

    os.remove(DATA_FILE)
    print(f"\n임시 파일 정리 완료: {DATA_FILE}")


if __name__ == "__main__":
    main()
