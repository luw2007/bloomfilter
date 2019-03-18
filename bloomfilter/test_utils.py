# coding: utf8

import os
import sys
sys.path.append(os.path.dirname(os.path.split(os.path.realpath(__file__))[0]))

import six
import unittest

from bloomfilter.utils import force_utf8


class TestUtils(unittest.TestCase):
    """工具方法测试"""

    def setUp(self):
        """setUp"""

    def tearDown(self):
        """tearDown"""
        pass

    def test_force_utf8(self):
        """测试force_utf8"""
        if six.PY3:
            self._assert_py3()
        else:
            self._assert_py2()

    def _assert_py2(self):
        """assert py2"""
        val_str = u'abc'
        val1 = force_utf8(val_str)
        self.assertEqual(val1, 'abc')

        val_tuple = (u'a', u'b', u'c')
        val2 = force_utf8(val_tuple)
        self.assertEqual(val2, ('a', 'b', 'c'))

        val_list = [u'a', u'b', u'c']
        val3 = force_utf8(val_list)
        self.assertEqual(val3, ['a', 'b', 'c'])

        val_dict = {'a': u'1', 'b': u'2'}
        val4 = force_utf8(val_dict)
        self.assertEqual(val4, {'a': '1', 'b': '2'})

    def _assert_py3(self):
        """assert py3"""
        val_str = 'abc'
        val1 = force_utf8(val_str)
        self.assertEqual(val1, b'abc')

        val_tuple = ('a', 'b', 'c')
        val2 = force_utf8(val_tuple)
        self.assertEqual(val2, (b'a', b'b', b'c'))

        val_list = ['a', 'b', 'c']
        val3 = force_utf8(val_list)
        self.assertEqual(val3, [b'a', b'b', b'c'])

        val_dict = {'a': '1', 'b': '2'}
        val4 = force_utf8(val_dict)
        self.assertEqual(val4, {'a': b'1', 'b': b'2'})


if __name__ == '__main__':
    unittest.main()
