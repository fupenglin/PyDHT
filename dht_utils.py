# -*- coding:utf-8 -*-


import os


# 节点ID总bit长
__node_id_bits__ = 160


# 随机生成20字节ID
def random_id():
    return os.urandom(__node_id_bits__ / 8)


