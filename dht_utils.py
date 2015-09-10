# -*- coding:utf-8 -*-


import os
import socket
import struct
import dht_bucket


# 节点ID总bit长
__node_id_bits__ = 160
# 会话ID总bit长
__tran_id_bits__ = 16


# 随机生成20字节ID
def random_id():
    return os.urandom(__node_id_bits__ / 8)


# 随机生成4字节tranid
def random_tranid():
    return os.urandom(__tran_id_bits__ / 8)


# 解析节点地址
def decode_nodes(data):
    nodes = []
    length = len(data)
    if length % 26 != 0:
        return nodes
    for idx in range(0, length, 26):
        nid = data[idx: idx + 20]
        nip = socket.inet_ntoa(data[idx + 20: idx + 24])
        nport = struct.unpack('!H', data[idx + 24: idx + 26])[0]
        nodes.append(dht_bucket.Node(nid, nip, nport))
    return nodes


def encode_nodes(nodes):
    data = ''
    for node in nodes:
        data += node.node_id
        print node.node_ip
        data += socket.inet_aton(node.node_ip)
        data += struct.pack('!H', node.node_port)
    return data
