import configparser
import threading, time
import pygame, sys
import csv
import socket, pickle
from pygame.locals import *

class SendThread(threading.Thread):
    def __init__(self,threadID,Player,serverconn):
        threading.Thread.__init__(self)
        self.ID = threadID
        self.Player = Player
        self.conn = serverconn
    def run(self):
        delay = 0.01
        def send(x,y):
            p = Packet(x, y)
            data = pickle.dumps(p)
            self.conn.s.sendto(data, (self.conn.IP,self.conn.TCP))
            time.sleep(delay)
        while 1:
            if pygame.key.get_pressed()[K_DOWN] != 0:
                y = self.Player.y + 1
                send(self.Player.x, y)
            if pygame.key.get_pressed()[K_UP] != 0:
                y = self.Player.y - 1
                send(self.Player.x, y)
            if pygame.key.get_pressed()[K_LEFT] != 0:
                x = self.Player.x - 1
                send(x, self.Player.y)
            if pygame.key.get_pressed()[K_RIGHT] != 0:
                x = self.Player.x + 1
                send(x, self.Player.y)


class RecvThread(threading.Thread):
    def __init__(self,threadID,Player,serverconn):
        threading.Thread.__init__(self)
        self.ID = threadID
        self.Player = Player
        self.others = dict()
        self.conn = serverconn
    def run(self):
        # self.conn.s.bind((self.conn.IP,self.conn.TCP))
        while 1:
            data = self.conn.s.recvfrom(10000)
            try:
                packet = pickle.loads(data[0])
                self.Player.Set_Coords(packet.x, packet.y)
                if not packet.others: continue
                for i in packet.others:
                    x = packet.others[i]["x"]
                    y = packet.others[i]["y"]
                    p = Player("enemy")
                    p.ID = i
                    p.Set_Coords(x, y)
                    p.Set_Color((0, 0, 255))
                    self.others[i] = p
            except: print("Whoops")


class Serverconn(object):
    def __init__(self,Binidng_IP,player):
        self.IP = Binidng_IP
        self.TCP = 5005
        self.Buffer = 1024
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        pack = Packet(0,0)
        data = pickle.dumps(pack)
        self.s.sendto(data, (self.IP,self.TCP))

class Packet(object):
    def __init__(self,x,y):
        self.x=x
        self.y=y

class Level(object):
    def load_file(self, filename="Main_Level.map"):
        self.map = []
        self.mapmap = []
        self.key = {}
        with open(filename) as file:
            for i in file.readlines():
                z = i.split(",")
                c = []
                for x in z:
                    c.append(int(x))
                self.map.append(c)
            self.width = len(self.map[0])
            self.height = len(self.map)

    def load_tile_table(self,filename,width,height):
        image = pygame.image.load(filename).convert()
        image_width, image_height = image.get_size()
        tile_table = []
        for tile_x in range(0, int(image_width / width)):
            line = []
            tile_table.append(line)
            for tile_y in range(0, int(image_height / height)):
                rect = (tile_x * width, tile_y * height, width, height)
                line.append(image.subsurface(rect))
        return tile_table

    def get_tile(self, x, y):
        try:
            char = self.map[y][x]
        except IndexError:
            return {}
        try:
            return self.key[char]
        except KeyError:
            return {}

    def calculate_fromtilemap(self,tile_table,number):
        width = len(tile_table)
        if number < width:
            return (number,0)
        else:
            acount = number // width
            z = number - (acount*width)
            return (z,acount)
        pass

    def Draw_Level(self,tile,screen):
        for y in range(self.height):
            for x in range(self.width):
                pos = self.calculate_fromtilemap(tile,self.map[y][x])
                screen.blit((tile[pos[0]][pos[1]]),(x*32,y*32))



class Player(object):
    def __init__(self,player_name):
        self.ID = 0
        self.name = player_name
        self.x = 0
        self.y = 0
        self.color = (255, 0, 0)

    def Set_Coords(self,x,y):
        self.x = x
        self.y = y

    def Set_Color(self,color):
        self.color = color


    def Draw(self,screen):
        pygame.draw.circle(screen, self.color, (self.x+10, self.y+10), 10)
        pos = pygame.mouse.get_pos()
        pygame.draw.line(screen, (0,0,0), (self.x+10,self.y+10), (pos))