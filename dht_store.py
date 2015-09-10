# -*- coding:utf-8 -*-


from threading import Thread
from Queue import Queue
import urllib2


class DHTStore(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.queue = Queue()
        self.is_working = True

    def run(self):
        while self.is_working:
            info_hash = self.queue.get()
            url = 'http://bt.box.n0808.com/' + info_hash[0:2] + '/' + info_hash[len(info_hash) - 2:] + '/' + info_hash + '.torrent'
            print url
            try:
                response = urllib2.urlopen(url)
                with open(info_hash, 'wb') as f:
                    f.write(response.read())
                    f.close()
            except Exception:
                pass

    def save_info_hash(self, info_hash):
        self.queue.put(info_hash.upper())

    def stop(self):
        self.is_working = False



if __name__ == '__main__':
    store = DHTStore()
    store.start()
    store.save_info_hash('6163B1A152E928BEA4146D354B2F5FCE4E781EB4')
