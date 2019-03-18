# coding: utf8
# pylint: disable=redefined-builtin,invalid-name

import six

if six.PY3:
    unicode = str


def force_utf8(data):
    """强转utf8

    :param data: data
    :return 转换后的数据
    """
    if isinstance(data, unicode):
        return _cover_utf8(data)
    elif isinstance(data, tuple):
        data = tuple([force_utf8(item) for item in data])
    elif isinstance(data, list):
        for idx, i in enumerate(data):
            data[idx] = force_utf8(i)
    elif isinstance(data, dict):
        for i in data:
            data[i] = force_utf8(data[i])
    return data


def _cover_utf8(value):
    """强转utf8

    :param value: value
    :return utf8类型的数据
    """
    return value.encode('utf8') \
        if isinstance(value, unicode) else value
