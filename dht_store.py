# -*- coding:utf-8 -*-


class DHTStore:

    def __init__(self, file_name):
        self.info_hash_cnt = 0
        self.file_name = file_name

    def save_info_hash(self, info_hash):
        self.info_hash_cnt += 1
        with open(self.file_name, 'a') as f:
            f.write(info_hash)
            f.close()


