import os

import pytest
import redis

from bloomfilter.base import BaseModel

pytestmark = pytest.mark.skipif(
    "BLOOMFILTER_REDIS_URL" not in os.environ,
    reason="BLOOMFILTER_REDIS_URL is not configured",
)


class IntegrationModel(BaseModel):
    PREFIX = "bf:integration"


def test_real_redis_round_trip():
    client = redis.Redis.from_url(os.environ["BLOOMFILTER_REDIS_URL"])
    model = IntegrationModel(client=client)
    model.delete()
    try:
        assert model.add("hello") == 1
        assert model.add("hello") == 0
        assert model.extend(["hello", "world"]) == 1
        assert model.contains("hello") is True
        assert model.contains(["hello", "missing", "world"]) == ["hello", "world"]
        assert model.keys() == [b"bf:integration.0"]
    finally:
        model.delete()
