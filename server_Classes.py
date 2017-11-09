import threading
import socket
import pickle
import time
import pygame, math
from random import randrange

class SendPacket(object):
    def __init__(self,X,Y,HP,bullets=list()):
        self.x = X
        self.hp = HP
        self.y = Y
        self.bullets = bullets
        self.others = dict()

class Player(object):
    def __init__(self,IP):
        self.IP = IP
        self.dead = False
    def Set_Coords(self,Coords):
        self.player_tank.x += Coords[0] * self.player_tank.spd
        self.player_tank.y += Coords[1] * self.player_tank.spd
        self.player_tank.Update_spr()
    def Create_Tank(self,x,y,Health,Speed,Firerate,Bullet_Damage,player_name):
        self.player_tank = Tank(x,y,Health,Speed,Firerate,Bullet_Damage,player_name)

class Serverconn(object):
    def __init__(self,Binidng_IP):
        self.IP = Binidng_IP
        self.TCP = 5005
        self.Buffer = 1024
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind((self.IP, self.TCP))

class Tank(object):
    def __init__(self,x,y,Health,Speed,Firerate,Bullet_Damage,player_name):
        self.name = player_name
        self.x = x
        self.y = y
        self.hp = Health
        self.spd = Speed
        self.fr = Firerate
        self.bd = Bullet_Damage
        self.bullets = []
        self.sprite = pygame.Rect((self.x,self.y,32,32))
    def Fire(self,tar_x,tar_y):
        _bullet = Bullet(self.x,self.y,tar_x,tar_y,self.spd)
        self.bullets.append(_bullet)
    def Update_spr(self):
        self.sprite = pygame.Rect((self.x, self.y, 32, 32))

class Bullet(object):
    def __init__(self,x,y,tar_x,tar_y,speed):
        self.x = x
        self.y = y
        self.tar_x = tar_x
        self.tar_y = tar_y
        self.speed = speed
        self.active = True
        delta_x = -(self.x - self.tar_x)
        delta_y = -(self.y - self.tar_y)
        self.angle= math.atan2(delta_y,delta_x)
        self.bulletspr = pygame.Rect((self.x + 5, self.y + 5, 10, 10))
        # self.angle = math.degrees(angle_rad)

    def Handle(self):
        self.bulletspr = pygame.Rect((self.x + 5, self.y + 5, 10, 10))
        if self.active == True:
            _x = math.sin(self.angle) * 6
            _y = math.cos(self.angle) * 6
            self.x += _y
            self.y += _x
        else:
            del self
    def Draw(self,screen):
        self.bulletspr = pygame.Rect((self.x+5, self.y+5,10,10))
        pygame.draw.rect(screen, (0, 0, 255), self.bulletspr)

class Socket_Listen_Thread(threading.Thread):
    def __init__(self,serverconn):
        threading.Thread.__init__(self)
        self.serverconn = serverconn
        self.action = {"UP":(0,-1),
                       "DOWN":(0,1),
                       "LEFT":(-1,0),
                       "RIGHT":(1,0)}
    def run(self):
        def check(p):
            while 1:
                try:
                    packet = pickle.loads(data)
                    break
                except:
                    pass
            if (p.dead == False):
                if (packet.text != "FIRE"):
                    p.Set_Coords(self.action[packet.text])
                else:
                    p.player_tank.Fire(packet.x,packet.y)

        adresses = []
        self.players = []
        self.thread_count = 0

        def checku():
            adresses.append(addr)
            p = Player(addr)
            while 1:
                try:
                    packet = pickle.loads(data)
                    break
                except:
                    pass
            x = randrange(0,800)
            y = randrange(0,800)
            p.Create_Tank(x,y,packet.hp,packet.spd,packet.fr,packet.bd,packet.name)
            self.players.append(p)

        while 1:
            data, addr = self.serverconn.s.recvfrom(1024)
            if addr in adresses:
                for p in self.players:
                    if p.IP == addr:
                        threading.Thread(target=check(p))
            else:
                if self.thread_count < 4:
                    threading.Thread(target=checku())
                    self.thread_count+=1

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