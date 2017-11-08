import threading
import socket
import pickle
import time

class SendPacket(object):
    def __init__(self,X,Y):
        self.x = X
        self.y = Y
        self.others = dict()

class Player(object):
    def __init__(self,IP):
        self.IP = IP
        self.x = 0
        self.y = 0
        self.Conn = 0
    def Set_Coords(self,X,Y):
        self.x = X
        self.y = Y
    def Set_Conn(self,Conn):
        self.Conn = Conn

class Serverconn(object):
    def __init__(self,Binidng_IP):
        self.IP = Binidng_IP
        self.TCP = 5005
        self.Buffer = 1024
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind((self.IP, self.TCP))

class Socket_Listen_Thread(threading.Thread):
    def __init__(self,serverconn):
        threading.Thread.__init__(self)
        self.serverconn = serverconn
    def run(self):
        def check(p):
            while 1:
                try:
                    packet = pickle.loads(data)
                    break
                except:
                    pass
            p.Set_Coords(packet.x, packet.y)

        adresses = []
        self.players = []
        thread_count = 0

        def checku():
            adresses.append(addr)
            p = Player(addr)
            while 1:
                try:
                    packet = pickle.loads(data)
                    break
                except:
                    pass
            p.Set_Coords(packet.x, packet.y)
            self.players.append(p)

        while 1:
            data, addr = self.serverconn.s.recvfrom(1024)
            if addr in adresses:
                for p in self.players:
                    if p.IP == addr:
                        threading.Thread(target=check(p))
            else:
                if thread_count < 3:
                    threading.Thread(target=checku())

class Connection_Listen_Thread(threading.Thread):
    def __init__(self,thread_ID,addr):
        threading.Thread.__init__(self)
        self.addr = addr
        self.player = Player(addr,thread_ID,addr)
        self.ID = thread_ID
    def run(self):
        while 1:
            data = self.conn.recv(1024)
            try:
                print(data)
                packet = pickle.loads(data)
                self.player.Set_Coords(packet.x,packet.y)
            except:
                print("whoops")