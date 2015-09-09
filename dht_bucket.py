# -*- coding:utf-8 -*-


class DHTBucket:

    def __init__(self):
        self.bucket = {}

    def update(self, nid, address):
        self.bucket[nid] = (nid, address)


