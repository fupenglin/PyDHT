# -*- coding:utf-8 -*-


import threading
import Queue
import socket
import dht_utils
import binascii
import dht_bencode


BTPROTOCOL = 'BitTorrent protocol'


class DHTTorrent(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.queue = Queue.Queue()

    def get_torrent(self, info_hash, address):
        self.queue.put((info_hash, address))

    def run(self):
        while True:
            info_hash, address = self.queue.get()
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                print 'created'
                sock.settimeout(10)
                sock.connect(address)

                # handshake 握手
                print 'sending'
                self.send_handshake_info(sock, info_hash)
                data = sock.recv(4096)
                print data
                if not self.check_handshake_info(data, info_hash):
                    print 'not ok'
                    continue

                # ext_handshake
                print 'sending ext_handshake'
                self.send_extend_handshake_info(sock)
                data = sock.recv(4096)
                print len(data)

            except Exception as e:
                print e.message
            finally:
                print 'socket close'
                sock.close()

    def send_handshake_info(self, sock, info_hash):
        pstr_len = 19
        pstr = BTPROTOCOL
        reserved = '\x00\x00\x00\x00\x00\x00\x00\x00'
        peer_id = dht_utils.random_id()
        data = chr(pstr_len) + pstr + reserved + info_hash + peer_id
        sock.send(data)

    def check_handshake_info(self, data, real_info_hah):

        pstr_len, data = ord(data[:1]), data[1:]
        print pstr_len
        if pstr_len != len(BTPROTOCOL):
            return False

        pstr, data = data[:pstr_len], data[pstr_len:]
        print pstr
        if pstr != BTPROTOCOL:
            return False

        info_hash = data[8:28]
        if info_hash != real_info_hah:
            return False

        return True

    def send_extend_handshake_info(self, sock):
        len = 1
        mid = 0
        data = chr(20) + chr(mid) + dht_bencode.encode({"m":{"ut_metadata": 1}})[1]
        print data
        sock.send(data)
