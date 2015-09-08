# -*- coding:utf-8 -*-


# 解析bencode数据
def decode(data, start_idx):
    if data[start_idx] == 'i':
        value, start_idx = __decode_int(data, start_idx + 1)
    elif data[start_idx].isdigit():
        value, start_idx = __decode_str(data, start_idx)
    elif data[start_idx] == 'l':
        value, start_idx = __decode_list(data, start_idx + 1)
    elif data[start_idx] == 'd':
        value, start_idx = __decode_dict(data, start_idx + 1)
    else:
        raise ValueError('data error!')
    return value, start_idx


# 解析整数
def __decode_int(data, start_idx):
    end_idx = data.index('e', start_idx)
    value = int(data[start_idx: end_idx])
    return value, end_idx + 1


#解析字符串
def __decode_str(data, start_idx):
    end_idx = data.index(':', start_idx)
    str_len = int(data[start_idx: end_idx])
    start_idx = end_idx + 1
    end_idx = start_idx + str_len
    value = data[start_idx: end_idx]
    return value, end_idx


#解析列表
def __decode_list(data, start_idx):
    values = []
    while data[start_idx] != 'e':
        value, start_idx = decode(data, start_idx)
        values.append(value)

    return values, start_idx + 1


#解析字典
def __decode_dict(data, start_idx):
    dict_value = {}
    while data[start_idx] != 'e':
        key, start_idx = decode(data, start_idx)
        value, start_idx = decode(data, start_idx)
        dict_value[key] = value
    return dict_value, start_idx + 1

