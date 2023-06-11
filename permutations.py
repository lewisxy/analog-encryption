import math
from typing import Callable, Any

def indexed_permutation(n: int, index: int) -> list:
    """given n and index in the range of [0, n!-1], return index's permutation of n using integers [0, n-1]"""
    lst = [x for x in range(n)]
    res = []
    while len(lst) > 0:
        idx = index // math.factorial(n - 1)
        res.append(lst[idx])
        lst.remove(lst[idx])
        index = index % math.factorial(n - 1)
        n -= 1
    return res

def permutation_index(permutation: list) -> int:
    """given a permutation using integers [0, n-1], return its index in the range of [0, n!-1]"""
    n = len(permutation)
    lst = [x for x in range(n)]
    index = 0
    for x in permutation:
        index += lst.index(x) * math.factorial(n - 1)
        lst.remove(x)
        n -= 1
    return index

def inverse(permutation: list) -> list:
    return [x[0] for x in sorted(enumerate(permutation), key=lambda x_: x_[1])]

def random_permutation(rnd_src_fn: Callable[[int], Any], n):
    size = math.factorial(n)
    # make sure to use sufficient amount of bytes to ensure uniformity
    bytes_needed = math.ceil(size.bit_length() / 8) + 4
    idx = int.from_bytes(rnd_src_fn(bytes_needed)) % size
    return indexed_permutation(n, idx)

# measure how good is a permutation by computing how far away, on average, each element moves
def average_distance(permutation: list) -> float:
    max_distance = math.floor(len(permutation) / 2) * len(permutation)
    return sum(abs(x - y) for x, y in enumerate(permutation)) / max_distance

if __name__ == "__main__":
    for i in range(math.factorial(5)):
        p = indexed_permutation(5, i)
        print(p)
        print(permutation_index(p))
    print(inverse([2, 0, 3, 1]))
