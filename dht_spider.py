# -*- coding:utf-8 -*-


import socket
import threading
import time
import dht_utils
import dht_bencode
import dht_bucket


# DHT网络中的超级节点
super_dht_nodes = [
    ("router.bittorrent.com", 6881),
    ("dht.transmissionbt.com", 6881),
    ("router.utorrent.com", 6881)
]


class DHTSpider(threading.Thread):

    is_working = False

    def __init__(self, server_id, server_port):
        threading.Thread.__init__(self)
        self.bucket = dht_bucket.DHTBucket()
        self.is_working = True
        self.server_id = server_id
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.bind(('0.0.0.0', server_port))
        self.listen_thread = threading.Thread(target=self.handle_message)
        self.handle_request = {
            'ping': self.handle_ping_request,
            'find_node': self.handle_get_peers_request,
            'get_peers': self.handle_get_peers_request,
            'announce_peer': self.handle_announce_request
        }

    def start(self):
        self.listen_thread.start()
        self.join_dht()

    def join_dht(self):
        for address in super_dht_nodes:
            self.process_find_node(dht_utils.random_id(), address)


    # 处理接收到的消息
    def handle_message(self):
        while self.is_working:
            try:
                print 'waiting....'
                data, address = self.sock.recvfrom(65536)
                ok, msg = dht_bencode.decode(data)
                if not ok:
                    continue
                if msg['y'] == 'r':
                    self.handle_response(msg, address)
                elif msg['y'] == 'q':
                    self.handle_request[msg['q']](msg, address)
                else:
                    pass
            except Exception as e:
                print 'error' + e.message
                pass

    # 处理find_node请求
    def handle_find_node_request(self, msg, address):
        print 'handle_find_node_request'
        pass

    # 处理ping请求
    def handle_ping_request(self, msg, address):
        print 'handle_ping_request'
        # 更新信息

        #  回复对方
        data = {
            't': msg['t'],
            'y': 'r',
            'r': {'id': self.server_id}
        }
        ok, reply_msg = dht_bencode.encode(data)
        if ok:
            self.sock.sendto(reply_msg, address)

    # 处理get_peers请求
    def handle_get_peers_request(self, msg, address):
        print 'handle_get_peers_request'
        pass

    # 处理announce请求
    def handle_announce_request(self, msg, address):
        print 'handle_announce_request'
        pass

    # 处理答复消息
    def handle_response(self, msg, address):
        print 'handle_response'
        nid = msg['r']['id']
        self.bucket.update(nid, address)
        nodes = dht_utils.decode_nodes(msg['r']['nodes'])
        for (nid, ip, port) in nodes:
            self.bucket.update(nid, (ip, port))
        pass

    def process_find_node(self, nid, address):
        data = {
            't': 'aa',
            'y': 'q',
            'q': 'find_node',
            'a': {'id': self.server_id, 'target': nid}
        }
        ok, query_msg = dht_bencode.encode(data)
        if ok:
            self.sock.sendto(query_msg, address)
            print 'sendto: ' + query_msg


if __name__ == '__main__':
    spider_id = dht_utils.random_id()
    spider_port = 6883
    spider = DHTSpider(spider_id, spider_port)
    spider.start()
    time.sleep(10)
    print spider.bucket.bucket
    print len(spider.bucket.bucket.items())