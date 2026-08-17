from unittest.mock import Mock

import fakeredis
import pytest
from redis.exceptions import ConnectionError

from bloomfilter.base import BaseModel


class Model(BaseModel):
    PREFIX = b"bf:model"


def test_base_model_proxy_supports_bytes_prefix_and_dunder_contains():
    model = Model(client=fakeredis.FakeRedis())
    assert model.bits == model.bf_conn.bits
    assert model.hashes == model.bf_conn.hashes
    assert model.add("hello") == 1
    assert "hello" in model
    assert model.keys() == [b"bf:model.0"]
    with pytest.raises(AttributeError):
        model.unknown_method()


def test_base_model_retries_then_raises_redis_error(monkeypatch):
    model = Model(client=fakeredis.FakeRedis())
    failing = Mock(side_effect=ConnectionError("offline"))
    monkeypatch.setattr(model.bf_conn, "add", failing)
    monkeypatch.setattr(model, "reconnect", Mock())

    with pytest.raises(ConnectionError, match="offline"):
        model.add("hello")

    assert failing.call_count == model.RETRIES
    assert model.reconnect.call_count == model.RETRIES


def test_backend_rejects_non_bytes_values_without_allocating():
    model = Model(client=fakeredis.FakeRedis())
    with pytest.raises(TypeError, match="str or bytes-like"):
        model.add(100_000_000)
