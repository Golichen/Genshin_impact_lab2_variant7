import itertools
from functools import reduce as functools_reduce

class HashMapSeparateChainingDict:
    def __init__(self, buckets=None, size=0, capacity=7):
        if buckets is None:
            self.buckets = tuple(() for _ in range(capacity))
        else:
            self.buckets = buckets
        self.size = size
        self.capacity = capacity

    def __eq__(self, other):
        if not isinstance(other, HashMapSeparateChainingDict):
            return False
        # 转换为字典比较内容，忽略顺序
        return dict(to_list(self)) == dict(to_list(other))
        # return dict(to_list(self)) == dict(to_list(other))

    def __str__(self):
        items = []
        for bucket in self.buckets:
            for key, value in bucket:
                items.append(f"{repr(key)}: {repr(value)}")
        return "{" + ", ".join(items) + "}"

    def __iter__(self):
        return iterator(self)

def cons(key, value, map):
    index = abs(hash(key)) % map.capacity
    bucket = map.buckets[index]
    new_bucket = replace_or_append(bucket, key, value)
    new_buckets = map.buckets[:index] + (new_bucket,) + map.buckets[index+1:]
    key_exists = any(existing_key == key for existing_key, _ in bucket)
    new_size = map.size if key_exists else map.size + 1
    return HashMapSeparateChainingDict(new_buckets, new_size, map.capacity)

def replace_or_append(bucket, key, value):
    if not bucket:
        return ((key, value),)
    current_key, current_val = bucket[0]
    if current_key == key:
        return ((key, value),) + bucket[1:]
    else:
        return (bucket[0],) + replace_or_append(bucket[1:], key, value)

def remove(map, key):
    index = abs(hash(key)) % map.capacity
    bucket = map.buckets[index]
    new_bucket = remove_from_bucket(bucket, key)
    if new_bucket == bucket:
        # 如果bucket未变化，说明键不存在
        raise KeyError(f"Key {key} not found")
    new_buckets = map.buckets[:index] + (new_bucket,) + map.buckets[index+1:]
    # key_existed = len(new_bucket) != len(bucket)
    new_size = map.size - 1 # if key_existed else map.size
    return HashMapSeparateChainingDict(new_buckets, new_size, map.capacity)

def remove_from_bucket(bucket, key):
    if not bucket:
        return ()
    current_key, current_val = bucket[0]
    if current_key == key:
        return bucket[1:]
    else:
        return (bucket[0],) + remove_from_bucket(bucket[1:], key)

def member(key, map):
    index = abs(hash(key)) % map.capacity
    bucket = map.buckets[index]
    return exists_in_bucket(bucket, key)

def exists_in_bucket(bucket, key):
    if not bucket:
        return False
    current_key, _ = bucket[0]
    return current_key == key or exists_in_bucket(bucket[1:], key)

def length(map):
    return map.size

def to_list(map):
    def process_buckets(buckets, acc):
        if not buckets:
            return acc
        current_bucket = buckets[0]
        new_acc = process_bucket(current_bucket, acc)
        return process_buckets(buckets[1:], new_acc)
    def process_bucket(bucket, acc):
        if not bucket:
            return acc
        return process_bucket(bucket[1:], acc + [bucket[0]])
    items = []
    for bucket in map.buckets:
        for key, value in bucket:
            items.append((key, value))
    # 按键的字符串表示排序，避免哈希值的不确定性
    items.sort(key=lambda x: str(x[0]))
    return items
    # return process_buckets(map.buckets, [])

def from_list(lst):
    def helper(lst, map):
        if not lst:
            return map
        key, value = lst[0]
        return helper(lst[1:], cons(key, value, map))
    return helper(lst, empty())

def concat(map1, map2):
    list1 = to_list(map1)
    list2 = to_list(map2)
    combined = list1 + list2
    return from_list(combined)

def empty():
    return HashMapSeparateChainingDict()

def filter(map, predicate):
    def helper(entries, acc):
        if not entries:
            return from_list(acc)
        key, value = entries[0]
        if predicate(key, value):
            return helper(entries[1:], acc + [(key, value)])
        else:
            return helper(entries[1:], acc)
    return helper(to_list(map), [])

def map_func(map, func):
    def helper(entries, acc):
        if not entries:
            return from_list(acc)
        key, value = entries[0]
        return helper(entries[1:], acc + [(key, func(value))])
    return helper(to_list(map), [])

def reduce(map, func, initial):
    def helper(entries, acc):
        if not entries:
            return acc
        key, value = entries[0]
        new_acc = func(acc, (key, value))
        return helper(entries[1:], new_acc)
    return helper(to_list(map), initial)

def iterator(map):
    def process_buckets(buckets):
        if not buckets:
            return
        yield from process_bucket(buckets[0])
        yield from process_buckets(buckets[1:])
    def process_bucket(bucket):
        if not bucket:
            return
        key, _ = bucket[0]
        yield key
        yield from process_bucket(bucket[1:])
    return process_buckets(map.buckets)
