import configparser
import threading, time
import pygame, sys
import csv
import eztext
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
        def send(value):
            if value == "FIRE":
                data = Packet(value)
                mousepos = pygame.mouse.get_pos()
                data.Set_Coords(mousepos[0],mousepos[1])
            else:
                data = Packet(value)
            self.conn.s.sendto(pickle.dumps(data), (self.conn.IP,self.conn.TCP))
            # time.sleep(delay)
        while 1:
            pygame.time.Clock().tick(60)
            if pygame.key.get_pressed()[K_DOWN] != 0:
                send("DOWN")
            if pygame.key.get_pressed()[K_UP] != 0:
                send("UP")
            if pygame.key.get_pressed()[K_LEFT] != 0:
                send("LEFT")
            if pygame.key.get_pressed()[K_RIGHT] != 0:
                send("RIGHT")
            if pygame.key.get_pressed()[K_SPACE] != 0:
                send("FIRE")

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
                    p = Player(packet.others[i]["name"])
                    p.ID = i
                    p.Create_Tank(x,y,0,0,0,0)
                    self.others[i] = p
            except: print("Whoops")

class Serverconn(object):
    def __init__(self,Binidng_IP,player):
        self.IP = Binidng_IP
        self.TCP = 5005
        self.Buffer = 1024
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        pack = player.player_tank
        data = pickle.dumps(pack)
        self.s.sendto(data, (self.IP,self.TCP))

class Packet(object):
    def __init__(self,text):
        self.text = text
    def Set_Coords(self,x,y):
        self.x = x
        self.y = y

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
        image = pygame.image.load(filename).convert_alpha()
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
        if number == -1:
            return 0
        elif number < width:
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
                if pos != 0:
                    screen.blit((tile[pos[0]][pos[1]]),(x*32,y*32))

class Player(object):
    def __init__(self,player_name):
        self.name = player_name

    def Create_Tank(self,x,y,Health,Speed,Firerate,Bullet_Damage):
        self.player_tank = Tank(x,y,Health,Speed,Firerate,Bullet_Damage,self.name)

    def Set_Coords(self,x,y):
        self.player_tank.x = x
        self.player_tank.y = y

    def Draw(self,screen,font):
        self.player_tank.Draw(screen,font)
        # pygame.draw.circle(screen, self.color, (self.x+10, self.y+10), 10)
        # pos = pygame.mouse.get_pos()
        # pygame.draw.line(screen, (0,0,0), (self.x+10,self.y+10), (pos))

class Tank(object):
    def __init__(self,x,y,Health,Speed,Firerate,Bullet_Damage,player_name):
        self.name = player_name
        self.x = x
        self.y = y
        self.hp = Health
        self.spd = Speed
        self.fr = Firerate
        self.bd = Bullet_Damage
    def Draw(self,screen,font):
        text = font.render(self.name, False, (0, 0, 0))
        spacing = text.get_rect().width / 2
        screen.blit(text,(self.x+10-spacing,self.y-20))
        pygame.draw.circle(screen, (0,0,0), (self.x + 10, self.y + 10), 10)

class Intro(object):
    def ipchooser(self):
        DISPLAYSURF = pygame.display.set_mode((800, 800))
        #Eerst het kopje IP adress:
        myfont = pygame.font.SysFont('MS Sans Serif', 100)
        starttext = myfont.render('IP adress', False, (255,255,255))
        #Dan het invullen van het ip adrea
        ip = eztext.Input(x=400, y= 350, color=(255, 255, 255), font=pygame.font.Font(None, 100))
        #De witte lijn onder het ip adres
        line = pygame.Rect((150, 410, 500, 10))
        #Submit knopje
        startbutton = pygame.Rect((300, 600, 200, 80))
        while True:
            DISPLAYSURF.fill((0, 0, 0))

            events = pygame.event.get()
            for event in events:
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if startbutton.collidepoint(mouse_pos):
                        print('button in ip chooser was pressed at {0}'.format(mouse_pos))
                        print(serverip)
                        pygame.mixer.music.stop()
                        return(serverip)
            ip.update(events)
            ip.draw(DISPLAYSURF)
            pygame.draw.rect(DISPLAYSURF, [255,255,255], line)
            DISPLAYSURF.blit(starttext, (252, 100))
            pygame.draw.rect(DISPLAYSURF, [0, 255, 0], startbutton)  # draw objects down here
            pygame.display.update()
            serverip = ip.value

    def __new__(cls):
        pygame.mixer.music.load("res/Menu.mp3")
        pygame.mixer.music.play(loops=-1, start=0.0)
        DISPLAYSURF = pygame.display.set_mode((800, 800))
        startbutton = pygame.Rect((325, 370, 150, 60))
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if startbutton.collidepoint(mouse_pos):
                        return (cls.ipchooser(cls))
            startimage = pygame.image.load("res/Start.png")
            DISPLAYSURF.blit(startimage, (325, 360))
            pygame.display.update()

class Music(object):
    pygame.init()
    def __init__(self):
        pygame.mixer.music.load("res/Backgroundmusic.mp3")
        pygame.mixer.music.play(-1, 0.0)