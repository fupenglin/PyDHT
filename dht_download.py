# -*- coding:utf-8 -*-


import urllib
import urllib2
import sqlite3
import io
import gzip


class DHTDownload:

    def __init__(self):
        self.db = sqlite3.connect('dht.db')
        self.cur = self.db.cursor()
        pass

    def test(self):
        for i in self.cur.execute('select info_hash from table_info'):
            print i
            try:
                info_hash = i[0]
                url = "http://bt.box.n0808.com/%s/%s/%s.torrent" % (info_hash[:2], info_hash[38:], info_hash)
                torrent = urllib2.urlopen(url, timeout=30)
                raw_data = torrent.read()
                self.save('torrents/' + info_hash + ".torrent", raw_data)
            except Exception as e:
                print 'error'
        self.db.close()

    def save(self, filename, content):

        try:
            file = open(filename, 'wb')
            file.write(content)
            file.close()
        except IOError,e:
            print e



if __name__ == '__main__':
    down = DHTDownload()
    down.test()


