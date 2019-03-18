# coding: utf8
# pylint: disable=invalid-name

from bloomfilter.base import BaseModel
from bloomfilter.conf import USER_READ

REDIS_CONF = {'host': '127.0.0.1', 'port': 6379, 'db': 0}
USER_READ = {
    'redis': REDIS_CONF,
    'key': 'bf:user_read',
    'size': 1000000,
}

class UserReadModel(BaseModel):
    """用户阅读时长过滤器"""

    PREFIX = USER_READ['key']
    BF_SIZE = USER_READ['size']

    def set(self, user_name):
        """用户更新了总阅读时长

        :param user_name: 用户名
        """
        return self.add(user_name)

    def is_set(self, user_name):
        """检查用户是否更新了总阅读时长

        :param user_name: 用户名
        """
        return self.contains(user_name)


user_read_filter = UserReadModel(redis=USER_READ['redis'])

if __name__ == "__main__":
    user_read_filter.set('i')
    user_read_filter.is_set('i')
