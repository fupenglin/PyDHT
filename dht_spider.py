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
        self.tran_cnt = 0

    # 启动DHT爬虫
    def start(self):
        self.listen_thread.start()
        self.join_dht()
        threading.Timer(5, self.send_ping_request).start()

    # 爬虫加入dht网络
    def join_dht(self):
        nodes = self.bucket.get_nodes()
        if len(nodes) < 500:
            for node in nodes:
                self.send_find_node(self.server_id, (node.node_ip, node.node_port))

            for address in super_dht_nodes:
                self.send_find_node(self.server_id, address)
        threading.Timer(30, self.join_dht).start()

    # 处理接收到的消息
    def handle_message(self):
        while self.is_working:
            try:
                #print 'waiting....'
                data, address = self.sock.recvfrom(65536)
                ok, msg = dht_bencode.decode(data)
                if not ok:
                    print 'decode error'
                    continue
                if msg['y'] == 'r':
                    self.handle_response(msg, address)
                elif msg['y'] == 'q':
                    self.handle_request[msg['q']](msg, address)
                elif msg['y'] == 'e':
                    print msg['e']
            except Exception as e:
                print 'error:' + e.message

    # 处理find_node请求
    def handle_find_node_request(self, msg, address):
        print 'handle_find_node_request'

        node = dht_bucket.Node(msg['a']['id'], *address)
        self.bucket.update(node.node_id, node)

        nodes = dht_utils.encode_nodes(self.bucket.get_kclose())
        data = {
            't': msg['t'],
            'y': 'r',
            'r': {'id': self.server_id, 'nodes': nodes}
        }
        ok, reply_msg = dht_bencode.encode(data)
        if ok:
            self.sock.sendto(reply_msg, address)

    # 处理ping请求
    def handle_ping_request(self, msg, address):
        print 'handle_ping_request'
        # 更新信息
        node = dht_bucket.Node(msg['a']['id'], *address)
        self.bucket.update(node.node_id, node)
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
        print 'info_hash: ' + dht_utils.id_to_hex(msg['a']['info_hash'])
        node = dht_bucket.Node(msg['a']['id'], *address)
        self.bucket.update(node.node_id, node)

        nodes = dht_utils.encode_nodes(self.bucket.get_kclose())
        data = {
            't': msg['t'],
            'y': 'r',
            'r': {'id': self.server_id, 'token': dht_utils.random_tranid(), 'nodes': nodes}
        }
        ok, reply_msg = dht_bencode.encode(data)
        if ok:
            self.sock.sendto(reply_msg, address)

    # 处理announce请求
    def handle_announce_request(self, msg, address):
        print 'handle_announce_request'
        print 'info_hash: ' + dht_utils.id_to_hex(msg['a']['info_hash'])
        node = dht_bucket.Node(msg['a']['id'], *address)
        self.bucket.update(node.node_id, node)

    # 处理答复消息
    def handle_response(self, msg, address):
        #print 'handle_response'
        self.bucket.pop_tran(msg['t'])
        nid = msg['r']['id']
        self.bucket.update(nid, dht_bucket.Node(nid, *address))
        if msg['r'].has_key('nodes'):
            nodes = dht_utils.decode_nodes(msg['r']['nodes'])
            for node in nodes:
                if node.node_id == self.server_id:
                    continue
                self.bucket.update(node.node_id, node)

    def send_find_node(self, nid, address):
        data = {
            't': dht_utils.random_tranid(),
            'y': 'q',
            'q': 'find_node',
            'a': {'id': self.server_id, 'target': nid}
        }
        ok, query_msg = dht_bencode.encode(data)
        if ok:
            self.sock.sendto(query_msg, address)

    def send_ping_request(self):
        print 'send_ping_request'
        nodes = self.bucket.get_nodes()
        print len(nodes)
        for node in nodes:
            tran_id = 'query_' + str(self.tran_cnt)
            self.tran_cnt = (self.tran_cnt + 1) % 2000
            self.bucket.add_tran(tran_id, node)
            data = {
                't': tran_id,
                'y': 'q',
                'q': 'ping',
                'a': {'id': self.server_id}
            }
            ok, query_msg = dht_bencode.encode(data)
            if ok:
                self.sock.sendto(query_msg, (node.node_ip, node.node_port))
        threading.Timer(60 * 10, self.send_ping_request).start()
        self.bucket.tran_time_out_action()

if __name__ == '__main__':
    spider_id = 'abcdefghij0123456789'
    spider_port = 6883
    spider = DHTSpider(spider_id, spider_port)
    spider.start()
