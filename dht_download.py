# -*- coding:utf-8 -*-


import urllib2
import MySQLdb
import dht_bencode


class DHTDownload:

    def __init__(self):
        self.conn = MySQLdb.connect(host='123.56.126.47', user='root', passwd='root', db='dht', port=3306, charset='UTF8')
        self.cur = self.conn.cursor()
        self.cur.execute("set names utf8")

    def test(self):
        self.cur.execute('select * from dht_info limit 18')
        for info in self.cur.fetchall():
            try:
                if info[1]:
                    t = info[1].decode('utf-8')
                   # continue
                info_hash = u'94E62A80A46EB05F01A6D6142FAE585F1F588455'
                url = "http://bt.box.n0808.com/%s/%s/%s.torrent" % (info_hash[:2], info_hash[38:], info_hash)
                torrent = urllib2.urlopen(url, timeout=10)
                raw_data = torrent.read()
                self.save(info_hash, raw_data)
            except Exception as e:
                print 'error'
        self.cur.close()
        self.conn.close()

    def save(self, info_hash, content):
        ok, msg = dht_bencode.decode(content)
        if not ok:
            return
        info = msg['info']['name'].decode('utf-8')
        sql = "update dht_info set dht_info.detail_info='%s' where dht_info.info_hash='%s'" % (info, info_hash)
        self.cur.execute(sql)


if __name__ == '__main__':
    down = DHTDownload()
    down.test()


