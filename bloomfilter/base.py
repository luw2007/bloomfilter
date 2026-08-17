import logging

from redis.exceptions import RedisError

from bloomfilter.backend import RedisBloom


class BaseModel:
    """Redis-backed Bloom filter compatible with pyreBloom's key layout."""

    SLOT = {"add", "contains", "extend", "keys", "put", "delete"}
    PREFIX = ""
    BF_SIZE = 100_000
    BF_ERROR = 0.01
    RETRIES = 2

    def __init__(self, redis=None, client=None):
        self._bf_conn = None
        self._client = client
        self._conf = {
            "host": "127.0.0.1",
            "password": "",
            "port": 6379,
            "db": 0,
            "socket_connect_timeout": 1.5,
            "socket_timeout": 1.5,
        }
        if redis:
            self._conf.update({key: value for key, value in redis.items() if key in self._conf})

    @property
    def bf_conn(self):
        if self._bf_conn is None:
            logging.debug(
                "RedisBloom connect: redis://%s:%s/%s, (%s %s %s)",
                self._conf["host"],
                self._conf["port"],
                self._conf["db"],
                self.PREFIX,
                self.BF_SIZE,
                self.BF_ERROR,
            )
            self._bf_conn = RedisBloom(
                self.PREFIX,
                self.BF_SIZE,
                self.BF_ERROR,
                client=self._client,
                **self._conf,
            )
        return self._bf_conn

    @property
    def bits(self):
        return self.bf_conn.bits

    @property
    def hashes(self):
        return self.bf_conn.hashes

    def __getattr__(self, method):
        if method not in self.SLOT:
            raise AttributeError(method)

        def call(*args, **kwargs):
            error = None
            for _ in range(self.RETRIES):
                try:
                    result = getattr(self.bf_conn, method)(*args, **kwargs)
                    if method == "contains" and isinstance(result, list):
                        return [item.decode() if isinstance(item, bytes) else item for item in result]
                    return result
                except RedisError as caught:
                    error = caught
                    logging.warning("RedisBloom error: %s %s", method, caught)
                    self.reconnect()
            raise error

        return call

    def __contains__(self, item):
        return self.contains(item)

    def reconnect(self):
        self._bf_conn = None
