# bloomfilter

Redis-backed Bloom filter for rejecting definite misses before database or cache lookups.

The pure-Python backend uses `redis-py` and preserves pyreBloom's MurmurHash64A seeds, bit layout, and `<prefix>.<index>` Redis key names. Existing filters written by pyreBloom remain readable when capacity, error rate, and prefix are unchanged.

## Install

```bash
python -m pip install .
```

Requirements: Python 3.9+ and Redis. No compiler, hiredis headers, or pyreBloom extension is required.

## Usage

```python
from bloomfilter.base import BaseModel


class UserFilter(BaseModel):
    PREFIX = "bf:users"
    BF_SIZE = 100_000
    BF_ERROR = 0.01


users = UserFilter(redis={"host": "127.0.0.1", "port": 6379, "db": 0})
users.add("alice")
assert users.contains("alice")
assert users.contains(["alice", "bob"]) == ["alice"]
users.delete()
```

Available methods: `add`, `put`, `extend`, `contains`, `keys`, and `delete`. `bits` and `hashes` expose the computed Bloom filter parameters.


Values and prefixes must be `str` or bytes-like objects. Numeric IDs should be converted explicitly, for example `users.add(str(user_id))`. Redis connect and read operations default to a 1.5-second timeout; pass `socket_connect_timeout` or `socket_timeout` through the Redis configuration only when a different bound is required.
## Compatibility

The backend intentionally matches pyreBloom's current storage format:

- MurmurHash64A with the same LCG-generated seeds
- the same bit and hash-count formulas
- Redis strings split at `0xFFFFFFFF` bits
- keys named `<prefix>.0`, `<prefix>.1`, and so on

Changing `PREFIX`, `BF_SIZE`, or `BF_ERROR` creates a different filter. Very old pyreBloom releases that predate deterministic LCG seeds are not compatible.

## Development

```bash
python -m pip install -e '.[test]'
pytest
```

The integration test requires `BLOOMFILTER_REDIS_URL`, for example `redis://127.0.0.1:6379/15`.

Design notes remain in [`doc/bloomfilter_in_action.md`](doc/bloomfilter_in_action.md) and [`doc/bloomfilter_principle.md`](doc/bloomfilter_principle.md).
