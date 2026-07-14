# poc-crud

두 가지 PoC(Proof of Concept)와, 이를 조합해 만든 JSON 파일 기반 CRUD 콘솔 애플리케이션을 담은 실습 프로젝트입니다.

## 실행 환경

- Python 3.13 (`.venv` 가상환경 포함)
- 앱 실행 자체는 외부 라이브러리 불필요 (표준 라이브러리만 사용)
- 테스트 실행에는 `pytest` 필요: `.venv/Scripts/python.exe -m pip install pytest`

```bash
.venv/Scripts/python.exe json_poc.py
.venv/Scripts/python.exe quick_sort_poc.py
.venv/Scripts/python.exe crud_app.py
```

Windows 콘솔에서 한글이 깨져 보이면 아래처럼 UTF-8 출력을 강제하세요.

```bash
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe json_poc.py
```

## 1. `json_poc.py` — JSON 파싱 / 저장 라이브러리 PoC

표준 `json` 모듈로 JSON 데이터를 다루는 기본 흐름을 검증합니다.

| 단계 | 내용 | 사용 함수 |
| --- | --- | --- |
| 1 | dict → JSON 문자열 (직렬화) | `json.dumps` |
| 2 | JSON 문자열 → dict (역직렬화) | `json.loads` |
| 3 | dict → JSON 파일 저장 | `json.dump` |
| 4 | JSON 파일 → dict 읽기 | `json.load` |
| 5 | 잘못된 형식의 JSON 파싱 시 에러 처리 | `json.JSONDecodeError` |
| 6 | `datetime` 등 기본으로 직렬화 안 되는 타입 처리 | `dumps(default=...)` |

**핵심 포인트**
- `ensure_ascii=False`를 줘야 한글이 유니코드 이스케이프(`\uXXXX`) 없이 그대로 저장됨.
- 잘못된 JSON은 예외(`JSONDecodeError`)로 실패하므로 반드시 `try/except`로 감싸야 함.
- `datetime`처럼 JSON이 기본 지원하지 않는 타입은 `default=` 콜백으로 직접 변환 로직을 지정해야 직렬화 가능.

## 2. `quick_sort_poc.py` — Quick Sort 알고리즘 PoC

퀵 정렬을 모른다고 가정하고, 원리부터 단계별로 구현합니다.

**핵심 아이디어**
1. 리스트에서 기준값(pivot)을 하나 고른다.
2. 나머지 값들을 pivot보다 작은 그룹(left) / 같은 그룹(mid) / 큰 그룹(right)으로 나눈다.
3. left, right에 대해 같은 과정을 재귀적으로 반복한다. 원소가 0~1개면 그 자체로 정렬 완료.
4. `정렬된 left + mid + 정렬된 right` 순서로 이어 붙이면 전체 정렬 완료.

평균 시간복잡도는 O(n log n)이며, pivot을 매번 최솟값/최댓값으로 뽑는 최악의 경우 O(n²)까지 느려질 수 있습니다.

**포함된 두 가지 구현**

| 구현 | 함수 | 특징 |
| --- | --- | --- |
| 설명용 구현 | `quick_sort_explained` | 리스트 컴프리헨션으로 분할, 메모리는 더 쓰지만 직관적 |
| in-place 구현 | `quick_sort_inplace` / `_partition` | Lomuto partition 방식, 원본 배열 내에서 교환하며 정렬 |

`demo()` 실행 시 두 구현의 결과를 파이썬 내장 `sorted()`와 비교 검증하고, 랜덤 데이터로 5회 반복 테스트를 수행합니다.

추가로, dict 리스트를 정렬할 수 있도록 일반화한 `quick_sort_by_key(items, key=...)` 함수도 포함되어 있습니다. 이 함수가 아래 CRUD 앱의 정렬 기능에 사용됩니다.

## 3. `crud_app.py` — JSON 파일 기반 회원 관리 CRUD 콘솔 앱

`json_poc.py`의 파일 입출력 패턴과 `quick_sort_poc.py`의 `quick_sort_by_key`를 조합해 만든 콘솔 애플리케이션입니다. 회원(id, name, age, email) 데이터를 `members.json` 파일에 저장하며 CRUD 전 기능을 제공합니다.

```bash
.venv/Scripts/python.exe crud_app.py
```

**메뉴 구성**

| 메뉴 | 기능 | 설명 |
| --- | --- | --- |
| 1 | 전체 조회 | id/name/age 중 정렬 기준과 asc/desc 순서를 선택해 목록 출력 (내부적으로 `quick_sort_by_key` 사용) |
| 2 | 추가 | 이름/나이/이메일 입력받아 새 회원 생성 (id는 기존 최대값+1로 자동 부여) |
| 3 | 단건 조회 | id로 특정 회원 검색 |
| 4 | 수정 | id로 회원을 찾아 이름/나이/이메일 중 원하는 값만 변경 (엔터 시 기존 값 유지) |
| 5 | 삭제 | id로 회원을 찾아 확인(y/N) 후 삭제 |
| 6 | 종료 | 앱 종료 |

**동작 방식**
- 앱 시작 시 `members.json`이 있으면 읽어오고, 없으면 빈 목록으로 시작.
- Create/Update/Delete가 일어날 때마다 즉시 `members.json`에 `json.dump(..., ensure_ascii=False, indent=2)`로 반영 (데이터 유실 방지).
- JSON 파일이 손상되어 파싱에 실패하면 에러를 내지 않고 빈 목록으로 안전하게 시작.
- 숫자 입력(id, 나이)은 `int()` 변환 실패 시 에러 메시지를 출력하고 해당 동작만 취소, 앱 자체는 종료되지 않음.

## 테스트 (Regression / Safety)

`tests/` 폴더에 `pytest` 기반 테스트 60개가 있습니다. 콘솔 입력(`input()`)이 필요한 함수는
`monkeypatch`로 입력을 흉내내고, 파일 입출력은 매 테스트마다 임시 경로(`tmp_path`)로
격리해 실제 `members.json`을 건드리지 않습니다.

```bash
.venv/Scripts/python.exe -m pip install pytest   # 최초 1회
.venv/Scripts/python.exe -m pytest -v
```

| 파일 | 검증 범위 |
| --- | --- |
| `tests/test_json_poc.py` | 직렬화/역직렬화/파일 입출력 round-trip, 잘못된 JSON 파싱 시 `JSONDecodeError` 발생(Safety), `datetime` 미지원 타입 처리, `main()` 전체 흐름 무결성(Regression) |
| `tests/test_quick_sort_poc.py` | 빈 리스트/중복값/음수/역순 등 경계값을 포함한 다양한 입력에서 세 구현 모두 `sorted()`와 결과 일치, 고정 시드 랜덤 회귀 테스트, `quick_sort_by_key`의 dict 정렬 동작 |
| `tests/test_crud_app.py` | Create/Read/Update/Delete 각 기능의 정상 동작과 파일 반영, 빈 이름·숫자 아닌 나이·존재하지 않는 id 등 잘못된 입력에서 앱이 죽지 않고 안전하게 무시/취소되는지, 생성→조회→수정→삭제 전체 플로우 회귀 테스트 |

**분류 기준**
- **Regression**: 정상 입력에서 기존 동작(정렬 결과, CRUD 결과, JSON round-trip)이 코드 변경 후에도 그대로 유지되는지 확인.
- **Safety**: 잘못되거나 예상 밖의 입력(깨진 JSON, 숫자가 아닌 나이, 존재하지 않는 id, 빈 이름 등)에 대해 앱이 예외로 죽지 않고 정의된 방식(에러 메시지 후 취소, 빈 목록 반환 등)으로 안전하게 반응하는지 확인.
