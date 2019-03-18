# coding=utf-8
'''
bloom filter 基础模块

可用方法:
extend, keys, contains, add, put, hashes, bits, delete

使用方法:
>>> class TestModel(BaseModel):
...    PREFIX = "bf:test"
>>> t = TestModel()
>>> t.add('hello')
1
>>> t.extend(['hi', 'world'])
2
>>> t.contains('hi')
True
>>> t.delete()

原生pyreBloom方法:

cdef class pyreBloom(object):

    cdef bloom.pyrebloomctxt context
    cdef bytes

	property bits:
	// redis中占用大小

	property hashes:
	// 使用的hash方法数

    def delete(self):
    // 删除，会在redis中删除

    def put(self, value):
    // 添加 底层方法, 不建议直接调用

    def add(self, value):
    // 添加单个元素，调用put方法

    def extend(self, values):
    // 添加一组元素，调用put方法

    def contains(self, value):
    // 检查是否存在，当`value`可以迭代时，返回`[value]`, 否则返回`bool`

    def keys(self):
    // 在redis中存储的key列表

'''
import logging
from six import PY3 as IS_PY3
from pyreBloom import pyreBloom, pyreBloomException

from bloomfilter.utils import force_utf8


class BaseModel(object):
    '''
    bloom filter 基础模块
    参数：
        SLOT: 可用方法类型
        PREFIX: redis前缀
        BF_SIZE: 存储最大值
        BF_ERROR: 允许的出错率
        RETRIES: 连接重试次数
        host: redis 服务器IP
        port: redis 服务器端口
        db: redis 服务器DB
        _bf_conn: 内部保存`pyreBloom`实例
    '''
    SLOT = {
        'add', 'contains', 'extend', 'keys', 'put', 'delete', 'bits', 'hashes'
    }
    PREFIX = ""
    BF_SIZE = 100000
    BF_ERROR = 0.01
    RETRIES = 2

    def __init__(self, redis=None):
        '''
        初始化redis配置
        :param redis: redis 配置
        '''
        # 这里初始化防止类静态变量多个继承类复用，导致数据被污染
        self._bf_conn = None

        self._conf = {
            'host': '127.0.0.1',
            'password': '',
            'port': 6379,
            'db': 0
        }

        if redis:
            for k, v in redis.items():
                if k in self._conf:
                    self._conf[k] = redis[k]
        self._conf = force_utf8(self._conf)

    @property
    def bf_conn(self):
        '''
        初始化pyreBloom
        '''
        if not self._bf_conn:
            prefix = force_utf8(self.PREFIX)
            logging.debug(
                'pyreBloom connect: redis://%s:%s/%s, (%s %s %s)',
                self._conf['host'],
                self._conf['port'],
                self._conf['db'],
                prefix,
                self.BF_SIZE,
                self.BF_ERROR,
            )
            self._bf_conn = pyreBloom(prefix, self.BF_SIZE, self.BF_ERROR,
                                      **self._conf)
        return self._bf_conn

    def __getattr__(self, method):
        '''调用pyrebloom方法
        没有枚举的方法将从`pyreBloom`中获取
        :param method:
        :return: pyreBloom.{method}
        '''
        # 只提供内部方法
        if method not in self.SLOT:
            raise NotImplementedError()

        # 捕获`pyreBloom`的异常, 打印必要的日志
        def catch_error(*a, **kwargs):
            '''多次重试服务'''
            args = force_utf8(a)
            kwargs = force_utf8(kwargs)
            for _ in range(self.RETRIES):
                try:
                    func = getattr(self.bf_conn, method)
                    res = func(*args, **kwargs)
                    # python3 返回值和python2返回值不相同，
                    # 手工处理返回类型
                    if method == 'contains' and IS_PY3:
                        if isinstance(res, list):
                            return [i.decode('utf8') for i in res]
                    return res
                except pyreBloomException as error:
                    logging.warn('pyreBloom Error:  %s %s', method, str(error))
                    self.reconnect()
                    if _ == self.RETRIES:
                        logging.error('pyreBloom Error')
                        raise error

        return catch_error

    def __contains__(self, item):
        '''跳转__contains__方法
        :param item: 查询元素列表/单个元素
        :type item: list/basestring
        :return: [bool...]/bool
        '''
        return self.contains(item)

    def reconnect(self):
        '''
        重新连接bloom
        `pyreBloom` 连接使用c driver，没有提供timeout参数，使用了内置的timeout
        同时为了保证服务的可靠性，增加了多次重试机制。
        ```
        struct timeval timeout = { 1, 5000 };
        ctxt->ctxt = redisConnectWithTimeout(host, port, timeout);
        ```
        del self._bf_conn 会调用`pyreBloom`内置的C的del方法，会关闭redis连接
        '''
        if self._bf_conn:
            logging.debug('pyreBloom reconnect')
            del self._bf_conn
            self._bf_conn = None
            _ = self.bf_conn
