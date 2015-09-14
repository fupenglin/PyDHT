# -*- coding:utf-8 -*-


import socket
import threading
import time
import dht_utils
import dht_bencode
import dht_bucket
import dht_store
import dht_torrent
import dht_config


# DHT网络中的超级节点
super_dht_nodes = [("router.bittorrent.com", 6881), ("dht.transmissionbt.com", 6881),("router.utorrent.com", 6881)]


class DHTSpider(threading.Thread):

    def __init__(self, server_id, server_port):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.is_working = True

        self.bucket = dht_bucket.DHTBucket()
        self.store = dht_store.DHTStore()
        self.torrent = dht_torrent.DHTTorrent()

        self.server_id = server_id
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.bind(('0.0.0.0', server_port))

        self.handle_request = {
            'ping': self.__handle_ping_request,
            'find_node': self.__handle_find_node_request,
            'get_peers': self.__handle_get_peers_request,
            'announce_peer': self.__handle_announce_request
        }
        self.tran_cnt = 0

    # 启动DHT爬虫
    def start_dht(self):
        self.start()
        self.store.start()
        self.torrent.start()
        self.__join_dht()
        threading.Timer(60 * 10, self.__send_ping_request).start()

    # 爬虫加入dht网络
    def __join_dht(self):
        rejoin_interval = 5 * 60    #默认重新加入dht网络的时间间隔为5分钟
        nodes = self.bucket.get_nodes()
        if len(nodes) < 1000:
            for node in nodes:
                self.__send_find_node(self.server_id, (node.node_ip, node.node_port))

            for address in super_dht_nodes:
                self.__send_find_node(self.server_id, address)
            rejoin_interval = 30    # 当路由表中节点的个数不满足要求时缩短时间间隔为30秒，以让节点快速加入dht网络

        threading.Timer(rejoin_interval, self.__join_dht).start()

    # 处理接收到的消息
    def run(self):
        while self.is_working:
            try:
                # 等待接收网络消息
                data, address = self.sock.recvfrom(65536)
                # 对消息进行解析以便处理应答
                ok, msg = dht_bencode.decode(data)
                if not ok: continue
                if msg['y'] == 'r':
                    self.__handle_response(msg, address)
                elif msg['y'] == 'q':
                    self.handle_request[msg['q']](msg, address)
            except Exception as e:
                pass

    # 处理find_node请求
    def __handle_find_node_request(self, msg, address):
        # 保存发送消息的节点信息到路由表
        node = dht_bucket.Node(msg['a']['id'], *address)
        self.bucket.update(node.node_id, node)

        # 获取k个与查询节点最近的节点信息作为应答
        nodes = dht_utils.encode_nodes(self.bucket.get_kclose())
        data = {
            't': msg['t'],
            'y': 'r',
            'r': {'id': self.server_id, 'nodes': nodes}
        }
        self.__send_message(data, address)

    # 处理ping请求
    def __handle_ping_request(self, msg, address):
        # 保存网络节点的ping请求，保存该结点信息
        node = dht_bucket.Node(msg['a']['id'], *address)
        self.bucket.update(node.node_id, node)

        # 回复节点的Ping请求,以保持在线状态
        data = {
            't': msg['t'],
            'y': 'r',
            'r': {'id': self.server_id}
        }
        self.__send_message(data, address)

    # 处理get_peers请求
    def __handle_get_peers_request(self, msg, address):
        # 接收到查询某个资源的请求，说明网络上可能存在该资源，因此保存该资源信息
        info = dht_store.SRC_INFO(dht_utils.id_to_hex(msg['a']['info_hash']), address[0], int(time.time()))
        self.store.save(info)

        # 更新或保存发送请求的节点信息
        node = dht_bucket.Node(msg['a']['id'], *address)
        self.bucket.update(node.node_id, node)

        # 答复该节点的请求，以便下接收到announce_peer消息
        nodes = dht_utils.encode_nodes(self.bucket.get_kclose())
        data = {
            't': msg['t'],
            'y': 'r',
            'r': {'id': self.server_id, 'token': dht_utils.random_tranid(), 'nodes': nodes}
        }
        self.__send_message(data, address)

    # 处理announce请求
    def __handle_announce_request(self, msg, address):

        if 'implied_port' in msg['a'].keys() and msg['a']['implied_port'] != 0:
            port = address[1]
        else:
            port = msg['a']['port']

        info = dht_store.SRC_INFO(dht_utils.id_to_hex(msg['a']['info_hash']), address[0] + ':' + str(port), int(time.time()))
        self.store.save(info)

        #self.torrent.get_torrent(msg['a']['info_hash'], (address[0], port))

        node = dht_bucket.Node(msg['a']['id'], *address)
        self.bucket.update(node.node_id, node)

    # 处理答复消息
    # DHT爬虫是不会发送get_peers请求和announce_peer请求的
    # 因此对于应答消息只有两种：find_node 和 ping
    def __handle_response(self, msg, address):
        # 保存或更新消息发送方的信息到路由表
        nid = msg['r']['id']
        self.bucket.update(nid, dht_bucket.Node(nid, *address))

        # 如果是Ping消息的应答，则应该删除该节点的ping请求超时设置
        if msg['t'] != 'find_node':
            self.bucket.pop_tran(msg['t'])

        # 保存find_node应答消息中的nodes信息到路由表
        if msg['r'].has_key('nodes'):
            nodes = dht_utils.decode_nodes(msg['r']['nodes'])
            for node in nodes:
                if node.node_id == self.server_id:
                    continue
                self.bucket.update(node.node_id, node)

    # 发送find_node请求
    def __send_find_node(self, nid, address):
        data = {
            't': 'find_node',
            'y': 'q',
            'q': 'find_node',
            'a': {'id': self.server_id, 'target': nid}
        }
        self.__send_message(data, address)

    # 发送ping请求
    def __send_ping_request(self):
        nodes = self.bucket.get_nodes()
        for node in nodes:
            tran_id = 'query_' + str(self.tran_cnt)
            self.tran_cnt = (self.tran_cnt + 1) % 20000
            self.bucket.add_tran(tran_id, node)
            data = {
                't': tran_id,
                'y': 'q',
                'q': 'ping',
                'a': {'id': self.server_id}
            }
            self.__send_message(data, (node.node_ip, node.node_port))
        threading.Timer(60 * 3, self.__send_ping_request).start()
        self.bucket.tran_time_out_action()

    # 向网络节点发送消息
    def __send_message(self, data, address):
        ok, query_msg = dht_bencode.encode(data)
        if ok:
            self.sock.sendto(query_msg, address)


if __name__ == '__main__':
    cf = dht_config.SpiderConfig()
    spider_id, spider_ip, spider_port = cf.get_spider(0)
    spider = DHTSpider(spider_id, spider_port)
    spider.start_dht()

