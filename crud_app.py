"""
JSON 파일 기반 CRUD 콘솔 애플리케이션

json_poc.py에서 검증한 "JSON 파싱/저장" 방식과
quick_sort_poc.py에서 검증한 "퀵 정렬" 알고리즘을 조합해서 만든
회원(members) 관리 콘솔 앱.

- 데이터는 members.json 파일 하나에 리스트[dict] 형태로 저장한다.
- Create/Read/Update/Delete 후에는 매번 파일에 즉시 반영(저장)한다.
- 목록 조회 시 quick_sort_by_key로 원하는 필드 기준 정렬을 지원한다.
"""

import json
import os

from quick_sort_poc import quick_sort_by_key

DATA_FILE = os.path.join(os.path.dirname(__file__), "members.json")
SORTABLE_FIELDS = ("id", "name", "age")


# ---------- JSON 파일 입출력 (json_poc.py 패턴 재사용) ----------

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print("경고: 데이터 파일이 손상되어 빈 목록으로 시작합니다.")
            return []


def save_data(members):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(members, f, ensure_ascii=False, indent=2)


# ---------- CRUD 로직 ----------

def next_id(members):
    if not members:
        return 1
    return max(m["id"] for m in members) + 1


def create_member(members):
    print("\n[회원 추가]")
    name = input("이름: ").strip()
    if not name:
        print("이름은 비워둘 수 없습니다.")
        return

    age = _read_int("나이: ")
    if age is None:
        return

    email = input("이메일: ").strip()

    member = {"id": next_id(members), "name": name, "age": age, "email": email}
    members.append(member)
    save_data(members)
    print(f"추가 완료: {member}")


def list_members(members):
    print("\n[전체 조회]")
    if not members:
        print("등록된 회원이 없습니다.")
        return

    field = input(f"정렬 기준 {SORTABLE_FIELDS} (엔터=id): ").strip() or "id"
    if field not in SORTABLE_FIELDS:
        print(f"'{field}'는 지원하지 않는 정렬 기준입니다. id 기준으로 정렬합니다.")
        field = "id"

    order = input("정렬 순서 (asc/desc, 엔터=asc): ").strip().lower() or "asc"

    sorted_members = quick_sort_by_key(members.copy(), key=lambda m: m[field])
    if order == "desc":
        sorted_members.reverse()

    _print_table(sorted_members)


def find_member(members):
    print("\n[단건 조회]")
    member_id = _read_int("조회할 회원 id: ")
    if member_id is None:
        return

    member = _find_by_id(members, member_id)
    if member is None:
        print(f"id={member_id} 회원을 찾을 수 없습니다.")
        return

    _print_table([member])


def update_member(members):
    print("\n[회원 수정]")
    member_id = _read_int("수정할 회원 id: ")
    if member_id is None:
        return

    member = _find_by_id(members, member_id)
    if member is None:
        print(f"id={member_id} 회원을 찾을 수 없습니다.")
        return

    print("변경하지 않으려면 엔터를 누르세요.")
    name = input(f"이름 ({member['name']}): ").strip()
    age_input = input(f"나이 ({member['age']}): ").strip()
    email = input(f"이메일 ({member['email']}): ").strip()

    if name:
        member["name"] = name
    if age_input:
        age = _parse_int(age_input)
        if age is None:
            print("나이는 숫자로 입력해야 합니다. 나이 변경은 취소되었습니다.")
        else:
            member["age"] = age
    if email:
        member["email"] = email

    save_data(members)
    print(f"수정 완료: {member}")


def delete_member(members):
    print("\n[회원 삭제]")
    member_id = _read_int("삭제할 회원 id: ")
    if member_id is None:
        return

    member = _find_by_id(members, member_id)
    if member is None:
        print(f"id={member_id} 회원을 찾을 수 없습니다.")
        return

    confirm = input(f"'{member['name']}'(id={member_id})를 삭제할까요? (y/N): ").strip().lower()
    if confirm != "y":
        print("삭제가 취소되었습니다.")
        return

    members.remove(member)
    save_data(members)
    print("삭제 완료")


# ---------- 헬퍼 ----------

def _find_by_id(members, member_id):
    for m in members:
        if m["id"] == member_id:
            return m
    return None


def _parse_int(text):
    try:
        return int(text)
    except ValueError:
        return None


def _read_int(prompt):
    value = _parse_int(input(prompt).strip())
    if value is None:
        print("숫자만 입력해야 합니다.")
    return value


def _print_table(members):
    header = f"{'id':<4}{'name':<12}{'age':<6}{'email':<25}"
    print(header)
    print("-" * len(header))
    for m in members:
        print(f"{m['id']:<4}{m['name']:<12}{m['age']:<6}{m['email']:<25}")


# ---------- 메인 메뉴 ----------

MENU = """
=== JSON 기반 회원 관리 CRUD ===
1. 전체 조회
2. 추가
3. 단건 조회
4. 수정
5. 삭제
6. 종료
"""


def main():
    members = load_data()

    actions = {
        "1": list_members,
        "2": create_member,
        "3": find_member,
        "4": update_member,
        "5": delete_member,
    }

    while True:
        print(MENU)
        choice = input("선택: ").strip()

        if choice == "6":
            print("종료합니다.")
            break

        action = actions.get(choice)
        if action is None:
            print("잘못된 선택입니다. 1~6 사이의 숫자를 입력하세요.")
            continue

        action(members)


if __name__ == "__main__":
    main()
