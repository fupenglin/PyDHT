# -*- coding:utf-8 -*-


def decode(data):
    try:
        value, idx = __decode(data, 0)
        retval = (True, value)
    except Exception as e:
        retval = (False, e.message)
    finally:
        return retval


def encode(data):
    try:
        value = __encode(data)
        retval = (True, value)
    except Exception, e:
        retval = (False, e.message)
    finally:
        return retval


# 内部函数
# 解析bencode数据
def __decode(data, start_idx):
    if data[start_idx] == 'i':
        value, start_idx = __decode_int(data, start_idx + 1)
    elif data[start_idx].isdigit():
        value, start_idx = __decode_str(data, start_idx)
    elif data[start_idx] == 'l':
        value, start_idx = __decode_list(data, start_idx + 1)
    elif data[start_idx] == 'd':
        value, start_idx = __decode_dict(data, start_idx + 1)
    else:
        raise ValueError('__decode: not in i, l, d')
    return value, start_idx


# 解析整数
def __decode_int(data, start_idx):
    end_idx = data.index('e', start_idx)
    try:
        value = int(data[start_idx: end_idx])
    except Exception:
        raise Exception('__decode_int: error')
    return value, end_idx + 1


# 解析字符串
def __decode_str(data, start_idx):
    try:
        end_idx = data.index(':', start_idx)
        str_len = int(data[start_idx: end_idx])
        start_idx = end_idx + 1
        end_idx = start_idx + str_len
        value = data[start_idx: end_idx]
    except Exception:
        raise Exception('__decode_str: error')
    return value, end_idx


# 解析列表
def __decode_list(data, start_idx):
    values = []
    while data[start_idx] != 'e':
        value, start_idx = __decode(data, start_idx)
        values.append(value)
    return values, start_idx + 1


# 解析字典
def __decode_dict(data, start_idx):
    dict_value = dict()
    while data[start_idx] != 'e':
        key, start_idx = __decode(data, start_idx)
        value, start_idx = __decode(data, start_idx)
        dict_value[key] = value
    return dict_value, start_idx + 1


# 数据编码
def __encode(data):
    if isinstance(data, int):
        value = __encode_int(data)
    elif isinstance(data, str):
        value = __encode_str(data)
    elif isinstance(data, dict):
        value = __encode_dict(data)
    elif isinstance(data, list):
        value = __encode_list(data)
    else:
        raise Exception('__encode: Error')
    return value


# 数字编码
def __encode_int(data):
    return 'i' + str(data) + 'e'


# 字符串编码
def __encode_str(data):
    str_len = len(data)
    return str(str_len) + ':' + data


# 列表编码
def __encode_list(data):
    ret = 'l'
    for datai in data:
        ret += __encode(datai)
    return ret + 'e'


# 字典编码
def __encode_dict(data):
    ret = 'd'
    for key, value in data.items():
        ret += __encode(key)
        ret += __encode(value)
    return ret + 'e'
