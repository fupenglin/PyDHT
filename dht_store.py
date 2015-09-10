# -*- coding:utf-8 -*-


from threading import Thread
from Queue import Queue


class DHTStore(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.queue = Queue()
        self.is_working = True

    def run(self):
        while self.is_working:
            info_hash = self.queue.get()
            print info_hash

    def save_info_hash(self, info_hash):
        self.queue.put(info_hash)

    def stop(self):
        self.is_working = False


