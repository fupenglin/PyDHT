# -*- coding:utf-8 -*-


class DHTStore:

    def __init__(self, file_name):
        self.info_hash_cnt = 0
        self.file_name = file_name

    def save_info_hash(self, info_hash):
        self.info_hash_cnt += 1
        with open(self.file_name, 'w') as f:
            f.write(self.info_hash_cnt)


