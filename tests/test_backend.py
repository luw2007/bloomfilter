import fakeredis

from bloomfilter.backend import RedisBloom, murmur_hash64a


def test_murmur_hash_matches_pyrebloom_reference_vectors():
    assert murmur_hash64a(b"hello", 314159265) == 2429813381808409957
    assert murmur_hash64a("你好".encode(), 1814548636) == 3383387914076070157


def test_redis_bloom_preserves_pyrebloom_key_layout_and_behavior():
    client = fakeredis.FakeRedis()
    bloom = RedisBloom("bf:test", 100_000, 0.01, client=client)

    assert bloom.keys() == [b"bf:test.0"]
    assert bloom.add("hello") == 1
    assert bloom.add("hello") == 0
    assert bloom.extend(["hello", "world"]) == 1
    assert bloom.contains("hello") is True
    assert bloom.contains(["hello", "missing", "world"]) == ["hello", "world"]

    bloom.delete()
    assert bloom.contains("hello") is False
