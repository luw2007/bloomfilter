import math
import struct

import redis

MASK64 = (1 << 64) - 1
MAX_BITS_PER_KEY = 0xFFFFFFFF


def _bytes(value):
    if isinstance(value, str):
        return value.encode()
    if isinstance(value, (bytes, bytearray, memoryview)):
        return bytes(value)
    raise TypeError(f"Bloom filter values must be str or bytes-like, got {type(value).__name__}")


def murmur_hash64a(data, seed):
    data = _bytes(data)
    multiplier = 0xC6A4A7935BD1E995
    shift = 47
    value = (seed ^ (len(data) * multiplier)) & MASK64

    block_end = len(data) - len(data) % 8
    for offset in range(0, block_end, 8):
        block = struct.unpack_from("<Q", data, offset)[0]
        block = (block * multiplier) & MASK64
        block ^= block >> shift
        block = (block * multiplier) & MASK64
        value ^= block
        value = (value * multiplier) & MASK64

    tail = data[block_end:]
    for index, byte in enumerate(tail):
        value ^= byte << (index * 8)
    if tail:
        value = (value * multiplier) & MASK64

    value ^= value >> shift
    value = (value * multiplier) & MASK64
    value ^= value >> shift
    return value


def _seeds(count):
    value = 314159265
    for _ in range(count):
        yield value
        value = (1664525 * value + 1013904223) & 0xFFFFFFFF


class RedisBloom:
    """Pure-Python backend compatible with pyreBloom's Redis representation."""

    def __init__(self, key, capacity, error, client=None, **redis_options):
        self.key = _bytes(key)
        self.capacity = capacity
        self.error = error
        self.bits = int(-(math.log(error) * capacity) / (math.log(2) ** 2))
        self.hashes = int(math.ceil(math.log(2) * self.bits / capacity))
        self._seeds = tuple(_seeds(self.hashes))
        self._keys = tuple(
            self.key + b"." + str(index).encode()
            for index in range(math.ceil(self.bits / MAX_BITS_PER_KEY))
        )
        redis_options.setdefault("socket_connect_timeout", 1.5)
        redis_options.setdefault("socket_timeout", 1.5)
        self.client = client or redis.Redis(**redis_options)

    def _locations(self, value):
        value = _bytes(value)
        for seed in self._seeds:
            offset = murmur_hash64a(value, seed) % self.bits
            yield self._keys[offset // MAX_BITS_PER_KEY], offset % MAX_BITS_PER_KEY

    def put(self, value):
        values = list(value) if isinstance(value, (list, tuple)) else [value]
        pipeline = self.client.pipeline(transaction=False)
        for item in values:
            for key, offset in self._locations(item):
                pipeline.setbit(key, offset, 1)
        replies = pipeline.execute()
        added = 0
        for index in range(0, len(replies), self.hashes):
            if not all(reply == 1 for reply in replies[index:index + self.hashes]):
                added += 1
        return added

    add = put

    def extend(self, values):
        return self.put(values)

    def contains(self, value):
        values = list(value) if isinstance(value, (list, tuple)) else [value]
        pipeline = self.client.pipeline(transaction=False)
        for item in values:
            for key, offset in self._locations(item):
                pipeline.getbit(key, offset)
        replies = pipeline.execute()
        included = []
        for index, item in enumerate(values):
            start = index * self.hashes
            if all(replies[start:start + self.hashes]):
                included.append(item)
        return included if isinstance(value, (list, tuple)) else bool(included)

    def delete(self):
        return self.client.delete(*self._keys)

    def keys(self):
        return list(self._keys)
