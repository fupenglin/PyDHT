# -*- coding:utf-8 -*-

import ConfigParser
import binascii


class SpiderConfig:

    def __init__(self):
        self.cf = ConfigParser.ConfigParser()
        self.cf.read('config.ini')

    def get_spider_cnt(self):
        return self.cf.getint('spider_global', 'spider_cnt')

    def get_spider(self, idx):
        section = 'spider_' + str(idx)
        spider_id = binascii.unhexlify(self.cf.get(section, 'spider_id'))
        spider_ip = self.cf.get(section, 'spider_ip')
        spider_port = self.cf.getint(section, 'spider_port')
        return spider_id, spider_ip, spider_port

    def get_spiders(self):
        spiders = []
        spider_cnt = self.get_spider_cnt()
        for idx in range(0, spider_cnt):
            spider = self.get_spider(idx)
            spiders.append(spider)
        return spiders
