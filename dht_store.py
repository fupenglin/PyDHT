# -*- coding:utf-8 -*-


import threading
import Queue
import MySQLdb



# 资源对象类
class SRC_INFO:

    def __init__(self, info_hash, from_ip, from_port, from_type, catch_time,):
        self.info_hash = info_hash.upper()
        self.from_ip = from_ip
        self.from_port = from_port
        self.from_type = from_type
        self.catch_time = catch_time


# 存储数据类
class DHTStore(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.queue = Queue.Queue()
        self.is_working = True
        self.info_hash_cnt = 0;
        try:
            self.conn = MySQLdb.connect(host='localhost', user='root', passwd='root', db='dht', port=3306, charset='UTF8')
            self.cur = self.conn.cursor()
        except MySQLdb.Error as e:
            pass

    def run(self):
        while self.is_working:
            size = self.queue.qsize()
            if not self.is_working:
                break;
            while size > 0:
                src = self.queue.get()
                self.cur.execute('insert ignore into dht_info(info_hash) values(%s)', src.info_hash)
                size -= 1
                self.info_hash_cnt += 1
            self.conn.commit()
        self.cur.close()
        self.conn.close()

    # 保存获取到的资源信息
    def save(self, info):
        self.queue.put(info)

    # 停止当前任务
    def stop(self):
        self.is_working = False
        self.save(None)

