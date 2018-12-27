#!/usr/bin/env python
import unittest
import socket
import time
import sys
import random

class BindSocketTest(unittest.TestCase):

    def setUp(self):
        self.port = self.getRandomPort()

    def getRandomPort(self):
        return random.randint(10000, 65535)

    # UDP AND TCP bind same port
    def testUdpTcp(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('', self.port))
        s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s2.bind(('', self.port))

    # TCP AND TCP bind same port
    def testTcpTcp(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', self.port))
        s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s2.bind(('', self.port))
        except socket.error as e:
            # socket.error: [Errno 98] Address already in use
            if e.errno != 98:
                raise e

    # TCP use tip
    def testTcpTip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', self.port))

        # set real server ip
        s.setsockopt(socket.SOL_IP, 22, socket.inet_aton('50.50.50.10'))

        # send to another ip with real server(50.50.50.10)'s mac address
        s.connect(('50.50.50.100', 80))

    # TCP use same tip and different rip
    def x_testTcpDaddrBucket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # set daddr to bind bucket
        s.setsockopt(socket.IPPROTO_IP, 95, socket.inet_aton('50.50.50.10'))
        s.bind(('', self.port))
        s.setsockopt(socket.SOL_IP, 22, socket.inet_aton('50.50.50.10'))
        s.connect(('50.50.50.100', 80))

        
        s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s2.setsockopt(socket.IPPROTO_IP, 95, socket.inet_aton('50.50.50.11'))
        s2.bind(('', self.port))
        s2.setsockopt(socket.SOL_IP, 22, socket.inet_aton('50.50.50.11'))
    
        '''
        This is critical problem.
        Expected result is connect fail. But s2.connect will succeed
        Because s and s2 have different bind bucket.
        Finally, s and s2 have same established bucket.
        ''' 
        s2.connect(('50.50.50.100', 80))

    # TCP_TW_RECYCLE
    def testTcpTwRecycle(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ret = s.getsockopt(socket.SOL_TCP, 98)
        assert ret == 0
        s.setsockopt(socket.SOL_TCP, 98, 1)
        ret = s.getsockopt(socket.SOL_TCP, 98)
        assert ret == 1
        s.bind(('', self.port))
        s.connect(('50.50.50.10', 80))


def SimpleServer():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 12345))
    s.listen(10)
    while True:
        conn, addr = s.accept()
        print conn, addr
        time.sleep(1)
        s.close()


if __name__ == '__main__':
    unittest.main()
