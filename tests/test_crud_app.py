"""
crud_app.py Regression / Safety 테스트

- Create/Read/Update/Delete가 각각 올바르게 동작하고 파일에 일관되게 반영되는지 (Regression)
- 잘못된 입력(빈 이름, 숫자가 아닌 나이, 존재하지 않는 id)에도 앱이 죽지 않고
  안전하게 무시/취소되는지 (Safety)
를 검증한다.

실제 콘솔 입력을 흉내내기 위해 builtins.input을 monkeypatch로 대체하고,
실제 프로젝트 데이터 파일(members.json)을 건드리지 않도록 DATA_FILE을
매 테스트마다 임시 경로로 바꿔치기한다.
"""

import builtins

import pytest

import crud_app


@pytest.fixture(autouse=True)
def isolate_data_file(tmp_path, monkeypatch):
    """모든 테스트가 실제 members.json이 아닌 임시 파일을 사용하도록 강제한다."""
    monkeypatch.setattr(crud_app, "DATA_FILE", str(tmp_path / "members.json"))
    yield


def _feed_inputs(monkeypatch, values):
    """input()이 호출될 때마다 values를 순서대로 반환하도록 흉내낸다."""
    responses = iter(values)
    monkeypatch.setattr(builtins, "input", lambda *_args: next(responses))


# ---------- 파일 입출력 ----------

def test_load_data_returns_empty_list_when_file_missing():
    assert crud_app.load_data() == []


def test_load_data_returns_empty_list_when_file_corrupted():
    with open(crud_app.DATA_FILE, "w", encoding="utf-8") as f:
        f.write("{not valid json")

    assert crud_app.load_data() == []


def test_save_and_load_roundtrip():
    members = [{"id": 1, "name": "Alice", "age": 30, "email": "a@test.com"}]
    crud_app.save_data(members)
    assert crud_app.load_data() == members


# ---------- id 채번 ----------

def test_next_id_starts_at_one_for_empty_list():
    assert crud_app.next_id([]) == 1


def test_next_id_increments_from_current_max():
    members = [{"id": 1}, {"id": 5}, {"id": 3}]
    assert crud_app.next_id(members) == 6


# ---------- Create ----------

def test_create_member_appends_and_persists_to_file(monkeypatch):
    members = []
    _feed_inputs(monkeypatch, ["Alice", "30", "alice@test.com"])

    crud_app.create_member(members)

    assert members == [{"id": 1, "name": "Alice", "age": 30, "email": "alice@test.com"}]
    assert crud_app.load_data() == members


def test_create_member_rejects_empty_name(monkeypatch):
    members = []
    _feed_inputs(monkeypatch, [""])

    crud_app.create_member(members)

    assert members == []


def test_create_member_rejects_non_numeric_age(monkeypatch):
    members = []
    _feed_inputs(monkeypatch, ["Alice", "not-a-number"])

    crud_app.create_member(members)

    assert members == []


# ---------- Read ----------

def test_find_by_id_returns_matching_member():
    members = [{"id": 1, "name": "Alice", "age": 30, "email": "a@test.com"}]
    assert crud_app._find_by_id(members, 1) == members[0]


def test_find_by_id_returns_none_for_unknown_id():
    members = [{"id": 1, "name": "Alice", "age": 30, "email": "a@test.com"}]
    assert crud_app._find_by_id(members, 999) is None


def test_list_members_sorts_by_requested_field(monkeypatch, capsys):
    members = [
        {"id": 1, "name": "Charlie", "age": 40, "email": "c@test.com"},
        {"id": 2, "name": "Alice", "age": 20, "email": "a@test.com"},
        {"id": 3, "name": "Bob", "age": 30, "email": "b@test.com"},
    ]
    _feed_inputs(monkeypatch, ["age", "asc"])

    crud_app.list_members(members)

    out = capsys.readouterr().out
    assert out.index("Alice") < out.index("Bob") < out.index("Charlie")


def test_list_members_invalid_sort_field_falls_back_to_id(monkeypatch, capsys):
    members = [
        {"id": 2, "name": "Bob", "age": 30, "email": "b@test.com"},
        {"id": 1, "name": "Alice", "age": 20, "email": "a@test.com"},
    ]
    _feed_inputs(monkeypatch, ["unknown_field", "asc"])

    crud_app.list_members(members)

    out = capsys.readouterr().out
    assert out.index("Alice") < out.index("Bob")


def test_list_members_handles_empty_list_without_error(capsys):
    crud_app.list_members([])
    assert "등록된 회원이 없습니다" in capsys.readouterr().out


# ---------- Update ----------

def test_update_member_changes_only_provided_fields(monkeypatch):
    members = [{"id": 1, "name": "Alice", "age": 30, "email": "a@test.com"}]
    crud_app.save_data(members)
    _feed_inputs(monkeypatch, ["1", "", "35", ""])  # id, name(유지), age(변경), email(유지)

    crud_app.update_member(members)

    assert members[0] == {"id": 1, "name": "Alice", "age": 35, "email": "a@test.com"}
    assert crud_app.load_data() == members


def test_update_member_unknown_id_leaves_data_untouched(monkeypatch):
    members = [{"id": 1, "name": "Alice", "age": 30, "email": "a@test.com"}]
    _feed_inputs(monkeypatch, ["999"])

    crud_app.update_member(members)

    assert members[0]["age"] == 30


def test_update_member_invalid_age_input_keeps_old_value(monkeypatch):
    members = [{"id": 1, "name": "Alice", "age": 30, "email": "a@test.com"}]
    _feed_inputs(monkeypatch, ["1", "", "not-a-number", ""])

    crud_app.update_member(members)

    assert members[0]["age"] == 30


# ---------- Delete ----------

def test_delete_member_removes_when_confirmed(monkeypatch):
    members = [{"id": 1, "name": "Alice", "age": 30, "email": "a@test.com"}]
    crud_app.save_data(members)
    _feed_inputs(monkeypatch, ["1", "y"])

    crud_app.delete_member(members)

    assert members == []
    assert crud_app.load_data() == []


def test_delete_member_keeps_record_when_not_confirmed(monkeypatch):
    members = [{"id": 1, "name": "Alice", "age": 30, "email": "a@test.com"}]
    _feed_inputs(monkeypatch, ["1", "n"])

    crud_app.delete_member(members)

    assert len(members) == 1


def test_delete_member_unknown_id_does_nothing(monkeypatch):
    members = [{"id": 1, "name": "Alice", "age": 30, "email": "a@test.com"}]
    _feed_inputs(monkeypatch, ["999"])

    crud_app.delete_member(members)

    assert len(members) == 1


# ---------- 통합 회귀 시나리오 ----------

def test_full_crud_regression_flow(monkeypatch):
    """생성 -> 조회 -> 수정 -> 삭제 전체 흐름이 매 단계 파일과 일관되는지 확인."""
    members = []

    _feed_inputs(monkeypatch, ["Alice", "30", "a@test.com"])
    crud_app.create_member(members)
    _feed_inputs(monkeypatch, ["Bob", "25", "b@test.com"])
    crud_app.create_member(members)

    assert crud_app.next_id(members) == 3
    assert crud_app.load_data() == members

    _feed_inputs(monkeypatch, ["2", "", "26", ""])
    crud_app.update_member(members)
    assert crud_app._find_by_id(members, 2)["age"] == 26
    assert crud_app.load_data() == members

    _feed_inputs(monkeypatch, ["1", "y"])
    crud_app.delete_member(members)
    assert crud_app._find_by_id(members, 1) is None
    assert crud_app.load_data() == members
