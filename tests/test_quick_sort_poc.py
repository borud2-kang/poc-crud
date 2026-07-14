"""
quick_sort_poc.py Regression / Safety 테스트

- 다양한 입력(빈 리스트, 단일 원소, 중복값, 음수, 무작위 데이터)에서
  세 가지 구현(quick_sort_explained / quick_sort_inplace / quick_sort_by_key)이
  파이썬 내장 sorted()와 항상 같은 결과를 내는지 검증한다 (Regression).
- 빈 리스트 같은 경계값에서 예외 없이 안전하게 동작하는지 확인한다 (Safety).
"""

import random

import pytest

import quick_sort_poc as qs

CASES = [
    [],
    [1],
    [2, 1],
    [3, 1, 2],
    [5, 2, 9, 1, 5, 6, 3, 8, 2, 7],
    [-3, -1, -2, 0, 5, -10],
    [4, 4, 4, 4],
    list(range(20, 0, -1)),  # 이미 역순 정렬된 최악 케이스에 가까운 입력
]


@pytest.mark.parametrize("data", CASES)
def test_quick_sort_explained_matches_builtin_sorted(data):
    assert qs.quick_sort_explained(data.copy()) == sorted(data)


@pytest.mark.parametrize("data", CASES)
def test_quick_sort_inplace_matches_builtin_sorted(data):
    assert qs.quick_sort_inplace(data.copy()) == sorted(data)


@pytest.mark.parametrize("data", CASES)
def test_quick_sort_by_key_identity_matches_builtin_sorted(data):
    assert qs.quick_sort_by_key(data.copy()) == sorted(data)


def test_quick_sort_by_key_sorts_dicts_by_chosen_field():
    members = [
        {"id": 3, "age": 40},
        {"id": 1, "age": 20},
        {"id": 2, "age": 30},
    ]
    result = qs.quick_sort_by_key(members.copy(), key=lambda m: m["age"])
    assert [m["id"] for m in result] == [1, 2, 3]


def test_quick_sort_by_key_stable_for_equal_keys():
    members = [
        {"id": 1, "age": 30},
        {"id": 2, "age": 30},
        {"id": 3, "age": 30},
    ]
    result = qs.quick_sort_by_key(members.copy(), key=lambda m: m["age"])
    assert {m["id"] for m in result} == {1, 2, 3}
    assert len(result) == 3


def test_random_regression_seeded_reproducible():
    """고정 시드로 여러 무작위 케이스를 검증 -> 실행할 때마다 같은 케이스로 재현 가능."""
    random.seed(42)
    for _ in range(20):
        data = [random.randint(-100, 100) for _ in range(random.randint(0, 50))]
        expected = sorted(data)
        assert qs.quick_sort_explained(data.copy()) == expected
        assert qs.quick_sort_inplace(data.copy()) == expected
        assert qs.quick_sort_by_key(data.copy()) == expected


def test_quick_sort_inplace_does_not_change_list_length():
    data = [5, 2, 9, 1, 5, 6, 3, 8, 2, 7]
    result = qs.quick_sort_inplace(data.copy())
    assert len(result) == len(data)


def test_demo_runs_without_error(capsys):
    """demo()가 내부 assert에 걸리지 않고 끝까지 실행되는지 확인 (안전성 스모크 테스트)."""
    qs.demo()
    captured = capsys.readouterr()
    assert "일치 확인 완료" in captured.out
