# -*- coding:utf-8 -*-


import threading
import Queue
import sqlite3
import time


# 资源对象类
class SRC_INFO:

    def __init__(self, info_hash, from_ip, catch_time):
        self.info_hash = info_hash.upper()
        self.from_ip = from_ip
        self.catch_time = catch_time


# 存储数据类
class DHTStore(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.queue = Queue.Queue()
        self.is_working = True

    def run(self):
        self.db = sqlite3.connect('dht.db')
        while self.is_working:
            size = self.queue.qsize()
            while size > 0:
                info = self.queue.get()
                self.db.execute("insert into table_info (info_hash, from_ip, catch_time) values (?, ?, ?)",
                                (info.info_hash, info.from_ip, info.catch_time))
                size -= 1
            self.db.commit()
        self.db.close()

    # 保存获取到的资源信息
    def save(self, info):
        self.queue.put(info)

    # 停止当前任务
    def stop(self):
        self.is_working = False
