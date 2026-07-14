"""
Quick Sort(퀵 정렬) PoC - 알고리즘을 전혀 모른다고 가정하고 단계별로 설명한다.

[핵심 아이디어]
  1. 리스트에서 기준값(pivot)을 하나 고른다. (여기서는 항상 "가운데" 값을 사용)
  2. 리스트의 나머지 값들을 pivot보다 작은 그룹(left), 같은 그룹(mid), 큰 그룹(right)
     세 덩어리로 나눈다.
  3. left와 right에 대해 각각 "1번부터 다시" 반복한다(재귀). 더 이상 나눌 게 없으면
     (원소가 0개나 1개면) 그 자체가 정렬된 상태이므로 재귀를 멈춘다.
  4. 마지막에 정렬된 left + mid + right 를 순서대로 이어 붙이면 전체가 정렬된다.

[왜 빠른가]
  - 한 번 나눌 때마다 pivot 하나는 "제자리"를 확정 짓고, 나머지는 절반씩(운이 좋으면)
    더 작은 문제로 쪼개진다. 그래서 평균적으로 O(n log n) 시간이 걸린다.
  - 최악의 경우(pivot을 항상 가장 작은/큰 값으로 고르면) O(n^2)까지 느려질 수 있다.
    이 PoC는 "가운데 인덱스"를 pivot으로 써서 최악의 경우를 어느 정도 피한다.

아래에는 이해를 돕기 위한 "설명용 구현"과, 실무에서 쓰는 "제자리(in-place) 구현"
두 가지를 함께 둔다.
"""

import random


def quick_sort_explained(items):
    """이해하기 쉬운 버전: 새 리스트를 만들어가며 분할한다 (메모리는 더 쓰지만 직관적)."""
    # 1. 종료 조건: 원소가 0개 또는 1개면 이미 정렬된 것과 같다.
    if len(items) <= 1:
        return items

    # 2. pivot(기준값) 선택: 가운데 인덱스의 값을 사용한다.
    pivot = items[len(items) // 2]

    # 3. pivot보다 작은 것 / 같은 것 / 큰 것으로 분류한다.
    left = [x for x in items if x < pivot]
    mid = [x for x in items if x == pivot]
    right = [x for x in items if x > pivot]

    # 4. left와 right를 각각 재귀적으로 정렬한 뒤, left + mid + right 순서로 합친다.
    return quick_sort_explained(left) + mid + quick_sort_explained(right)


def quick_sort_by_key(items, key=lambda x: x):
    """
    dict 같은 비교 불가능한 객체도 정렬할 수 있도록 만든 범용 버전.
    quick_sort_explained와 원리는 동일하되, 비교 시 `key(x)`로 뽑아낸 값을 기준으로 삼는다.
    예: quick_sort_by_key(members, key=lambda m: m["age"])
    """
    if len(items) <= 1:
        return items

    pivot_value = key(items[len(items) // 2])

    left = [x for x in items if key(x) < pivot_value]
    mid = [x for x in items if key(x) == pivot_value]
    right = [x for x in items if key(x) > pivot_value]

    return quick_sort_by_key(left, key) + mid + quick_sort_by_key(right, key)


def quick_sort_inplace(items, low=0, high=None):
    """실무형 in-place(제자리) 구현: 별도 리스트를 만들지 않고 원본 배열 안에서 교환한다."""
    if high is None:
        high = len(items) - 1

    if low >= high:
        return items

    pivot_index = _partition(items, low, high)
    quick_sort_inplace(items, low, pivot_index - 1)
    quick_sort_inplace(items, pivot_index + 1, high)
    return items


def _partition(items, low, high):
    """
    Lomuto partition 방식:
      - 맨 오른쪽(high) 값을 pivot으로 삼는다.
      - pivot보다 작은 값들을 왼쪽으로 몰아넣고, 마지막에 pivot을 그 경계 자리로 옮긴다.
      - 반환값은 pivot이 최종적으로 자리잡은 인덱스.
    """
    pivot = items[high]
    boundary = low - 1  # "pivot보다 작은 값들의 마지막 위치"를 가리키는 포인터

    for current in range(low, high):
        if items[current] <= pivot:
            boundary += 1
            items[boundary], items[current] = items[current], items[boundary]

    items[boundary + 1], items[high] = items[high], items[boundary + 1]
    return boundary + 1


def demo():
    sample = [5, 2, 9, 1, 5, 6, 3, 8, 2, 7]
    print(f"원본 리스트: {sample}")

    result1 = quick_sort_explained(sample.copy())
    print(f"[설명용 구현] 정렬 결과: {result1}")

    result2 = quick_sort_inplace(sample.copy())
    print(f"[in-place 구현] 정렬 결과: {result2}")

    assert result1 == result2 == sorted(sample), "정렬 결과가 서로 다릅니다!"
    print("두 구현 모두 파이썬 내장 sorted()와 결과 일치 확인 완료")

    # 무작위 데이터로 여러 번 검증
    for trial in range(5):
        data = [random.randint(-50, 50) for _ in range(random.randint(0, 30))]
        expected = sorted(data)
        got_explained = quick_sort_explained(data.copy())
        got_inplace = quick_sort_inplace(data.copy())
        assert got_explained == expected, f"설명용 구현 실패: {data}"
        assert got_inplace == expected, f"in-place 구현 실패: {data}"
        print(f"랜덤 테스트 {trial + 1}: 원소 {len(data)}개 - 통과")


if __name__ == "__main__":
    demo()
