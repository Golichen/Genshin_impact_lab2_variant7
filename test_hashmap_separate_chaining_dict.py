import pytest
import hypothesis.strategies as st
from hypothesis import given
from hashmap_separate_chaining_dict import (
    HashMapSeparateChainingDict,
    cons,
    remove,
    member,
    length,
    to_list,
    from_list,
    concat,
    filter,
    map_func,
    reduce,
    empty,
)

# Helper strategies for Hypothesis
keys = st.one_of(st.integers(), st.text(), st.booleans())
values = st.one_of(st.integers(), st.text(), st.booleans())
key_value_pairs = st.tuples(keys, values)

# ------------------- Base Functionality Tests -------------------

def test_empty():
    m = empty()
    assert length(m) == 0
    assert to_list(m) == []


def test_cons_basic():
    m = cons("a", 1, empty())
    assert member("a", m)
    assert length(m) == 1
    assert to_list(m) == [("a", 1)]


def test_cons_overwrite():
    m1 = cons("a", 1, empty())
    m2 = cons("a", 2, m1)
    assert member("a", m2)
    assert to_list(m2) == [("a", 2)]


def test_remove_existing():
    m = from_list([("a", 1), ("b", 2)])
    m_new = remove(m, "a")
    assert not member("a", m_new)
    assert member("b", m_new)
    assert length(m_new) == 1


def test_remove_non_existing():
    m = from_list([("a", 1)])
    with pytest.raises(KeyError):
        remove(m, "b")


def test_member():
    m = from_list([(1, "x"), ("key", "value")])
    assert member(1, m)
    assert member("key", m)
    assert not member(999, m)


def test_concat():
    m1 = from_list([("a", 1), ("b", 2)])
    m2 = from_list([("b", 20), ("c", 3)])
    merged = concat(m1, m2)
    # 按排序后的顺序断言
    expected = sorted([("a", 1), ("b", 20), ("c", 3)], key=lambda x: str(x[0]))
    assert sorted(to_list(merged), key=lambda x: str(x[0])) == expected


def test_filter():
    def pred(k, v):
        return isinstance(k, int) and v % 2 == 0
    m = from_list([(1, 2), (2, 3), ("a", 4)])
    filtered = filter(m, pred)
    assert to_list(filtered) == [(1, 2)]


def test_map():
    m = from_list([("a", 1), ("b", 2)])
    mapped = map_func(m, lambda x: x * 10)
    # 按排序后的顺序断言
    expected = sorted([("a", 10), ("b", 20)], key=lambda x: str(x[0]))
    assert sorted(to_list(mapped), key=lambda x: str(x[0])) == expected


def test_reduce():
    m = from_list([(1, "a"), (2, "b")])
    result = reduce(m, lambda acc, kv: acc + kv[1], "")
    assert result == "ab"


def test_equality():
    m1 = from_list([(1, "a"), (2, "b")])
    m2 = from_list([(2, "b"), (1, "a")])  # Order shouldn't matter
    assert m1 == m2


def test_str_representation():
    m = from_list([("a", 1), (2, "b")])
    assert str(m) == "{'a': 1, 2: 'b'}" or str(m) == "{2: 'b', 'a': 1}"

# ------------------- Property-Based Tests -------------------

@given(st.lists(key_value_pairs, unique_by=lambda x: x[0]))
def test_from_list_to_list_equality(lst):
    m = from_list(lst)
    # 转换为字典比较内容，忽略顺序
    assert dict(to_list(m)) == dict(lst)


@given(st.lists(key_value_pairs), st.lists(key_value_pairs))
def test_concat_property(lst1, lst2):
    m1 = from_list(lst1)
    m2 = from_list(lst2)
    merged = concat(m1, m2)
    # Last occurrence of each key should persist
    expected_dict = dict(lst1 + lst2)
    assert dict(to_list(merged)) == expected_dict


@given(st.lists(key_value_pairs))
def test_immutability_after_operations(lst):
    original = from_list(lst)
    modified = cons("test_key", "test_val", original)
    assert original != modified  # New instance created
    assert not member("test_key", original)


@given(st.lists(key_value_pairs))
def test_monoid_identity(lst):
    m = from_list(lst)
    assert concat(empty(), m) == m
    assert concat(m, empty()) == m


@given(st.lists(key_value_pairs))
def test_filter_property(lst):
    def pred(k, v):
        return hash(k) % 2 == 0  # Arbitrary predicate
    m = from_list(lst)
    filtered = filter(m, pred)
    for k, v in to_list(filtered):
        assert pred(k, v)

# ------------------- Iterator Tests -------------------

def test_iterator():
    m = from_list([("a", 1), (2, "b"), (None, "c")])
    keys = []
    try:
        it = m.__iter__()
        while True:
            keys.append(next(it))
    except StopIteration:
        pass
    assert set(keys) == {"a", 2, None}
    assert len(keys) == 3  # No duplicates


def test_empty_iterator():
    m = empty()
    it = m.__iter__()
    with pytest.raises(StopIteration):
        next(it)
