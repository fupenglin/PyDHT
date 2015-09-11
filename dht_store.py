# -*- coding:utf-8 -*-


import threading
import Queue
import sqlite3


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
                info_hash = self.queue.get()
                self.db.execute("insert into table_info (info_hash) values (?)", [info_hash])
                size -= 1
            self.db.commit()

    def save_info_hash(self, info_hash):
        self.queue.put(info_hash.upper())

    def stop(self):
        self.is_working = False

