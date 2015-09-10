# -*- coding:utf-8 -*-


from threading import Timer


class Node:

    def __init__(self, node_id, node_ip, node_port):
        self.node_id = node_id
        self.node_ip = node_ip
        self.node_port = node_port


# route table
class DHTBucket:

    def __init__(self):
        self.__bucket = {}
        self.__tran_bucket = {}

    def update(self, node_id, node):
        if len(self.__bucket.keys()) <= 2000:
            self.__bucket[node_id] = node

    def delete(self, node_id):
        if self.__bucket.has_key(node_id):
            self.__bucket.pop(node_id)

    def get_nodes(self):
        return self.__bucket.values()

    def get_kclose(self):
        return self.__bucket.values()[: 8]

    def add_tran(self, tran_id, node):
        self.__tran_bucket[tran_id] = node

    def pop_tran(self, tran_id):
        if self.__tran_bucket.has_key(tran_id):
            return self.__tran_bucket.pop(tran_id)
        else:
            return None

    def tran_time_out_action(self):
        for node in self.__tran_bucket.values():
            print 'delete node'
            if self.__bucket.has_key(node.node_id):
                self.__bucket.pop(node.node_id)

    def tran_timer_start(self):
        Timer(10, self.tran_time_out_action).start()


