# coding=utf-8
'''
测试使用的基类
使用方法:

from bloomfilter import mock_bloomfilter
mock_bloomfilter()

'''

def mock_bloomfilter():
    '''monkey patch'''
    import bloomfilter.base
    bloomfilter.base.BaseModel = MockBaseModel


class MockBaseModel(object):
    '''模拟pyreBloom
        'add', 'contains', 'extend', 'keys', 'put', 'bits', 'hashes'
    '''
    _instance = None

    def __new__(cls, *args, **kwargs):
        '''实现单例'''
        if not cls._instance:
            cls._instance = super(MockBaseModel, cls).__new__(
                cls, *args, **kwargs)
        return cls._instance

    def __init__(self, redis=None):
        '''初始化redis配置'''
        if not redis:
            redis = {'host': '127.0.0.1', 'port': 6379, 'db': 0}
        self.host = redis['host']
        self.port = redis['port']
        self.db = redis['db']
        self._cache = set()

    def add(self, items):
        '''添加'''
        if isinstance(items, (tuple, list)):
            result = [item for item in items if item not in self._cache]
            for i in result:
                self._cache.add(i)
            return len(result)
        else:
            if items in self._cache:
                return 0
            else:
                self._cache.add(items)
                return 1

    def contains(self, items):
        '''检查是否存在'''
        if isinstance(items, (tuple, list)):
            return [item for item in items if item in self._cache]
        else:
            return items in self._cache

    def delete(self):
        '''清理'''
        self._cache = set()

    def extend(self, items):
        '''批量添加'''
        return sum(self.add(item) for item in items)

    def keys(self):
        """ Return a list of the keys used in this bloom filter """
        return []

    def __contains__(self, item):
        """ x.__contains__(y) <==> y in x """
        return self.contains(item)

    bits = property(lambda self: object(), lambda self, v: None,
                    lambda self: None)

    hashes = property(lambda self: object(), lambda self, v: None,
                      lambda self: None)
