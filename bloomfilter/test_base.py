# coding=utf-8
from unittest import TestCase

from bloomfilter.base import BaseModel
from bloomfilter.mock import MockBaseModel


class CommonModel(BaseModel):
    '''普通model'''
    PREFIX = "bf:test"


class CommonMockModel(MockBaseModel):
    '''mock model'''
    PREFIX = "bf:mock"


class TestBaseModel(TestCase):
    '''测试基本方法'''

    def setUp(self):
        '''初始化'''
        self.p = CommonModel()

    def tearDown(self):
        '''删除'''
        self.p.delete()

    def test_common(self):
        '''测试'''
        self.assertEqual(self.p.add('one'), 1)
        self.assertEqual(self.p.contains('one'), True)

        # 重复添加
        self.assertEqual(self.p.add('one'), 0)

        # 不存在查询
        self.assertEqual(self.p.contains('two'), False)

        # 批量添加后查询
        self.assertEqual(self.p.extend(['one', 'three']), 1)
        self.assertEqual(self.p.extend(['four', 'five']), 2)
        self.assertEqual(
            self.p.contains(['one', 'two', 'three']), ['one', 'three'])

        # 删除后查询
        self.p.delete()
        self.assertEqual(self.p.contains('one'), False)


class TestMockBaseModel(TestBaseModel):
    '''测试mock方法'''

    def setUp(self):
        '''初始化'''
        self.p = CommonMockModel()

    def tearDown(self):
        '''删除'''
        self.p.delete()
