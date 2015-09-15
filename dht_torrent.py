# -*- coding:utf-8 -*-


import threading
import Queue
import socket
import struct
import dht_utils
import binascii
import dht_bencode


BT_PROTOCOL = 'BitTorrent protocol'


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
                print struct.unpack("<I", data[:4])[0]
                print len(data)

            except Exception as e:
                print e.message
            finally:
                print 'socket close'
                sock.close()
                break;

    def send_handshake_info(self, sock, info_hash):
        pstr_len = 19
        pstr = BT_PROTOCOL
        reserved = '\x00\x00\x00\x00\x00\x00\x00\x00'
        peer_id = dht_utils.random_id()
        data = chr(pstr_len) + pstr + reserved + info_hash + peer_id
        sock.send(data)

    def check_handshake_info(self, data, real_info_hah):

        pstr_len, data = ord(data[:1]), data[1:]
        print pstr_len
        if pstr_len != len(BT_PROTOCOL):
            return False

        pstr, data = data[:pstr_len], data[pstr_len:]
        print pstr
        if pstr != BT_PROTOCOL:
            return False

        info_hash = data[8:28]
        if info_hash != real_info_hah:
            return False

        return True

    def send_extend_handshake_info(self, sock):
        data = chr(20) + chr(0) + dht_bencode.encode({"m": {"ut_metadata": 1}})[1]
        self.__send_msg(sock, data)

    def __send_msg(self, sock, data):
        msg = struct.pack('>I', len(data)) + data
        sock.send(msg)

if __name__ == '__main__':
    torrent = DHTTorrent()
    torrent.get_torrent(binascii.unhexlify('9462C5B3DB1527F60985426C09CB57A0F2A6C0D6'), ("120.210.179.164", 6881))
    torrent.run()
