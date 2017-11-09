import configparser
import threading, time
import pygame, sys
import csv
import eztext
import random
import socket, pickle, math
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
        count = 0
        while 1:
            pygame.time.Clock().tick(60)
            if pygame.key.get_pressed()[K_s] != 0:
                send("DOWN")
            if pygame.key.get_pressed()[K_w] != 0:
                send("UP")
            if pygame.key.get_pressed()[K_a] != 0:
                send("LEFT")
            if pygame.key.get_pressed()[K_d] != 0:
                send("RIGHT")
            if pygame.key.get_pressed()[K_SPACE] != 0:
                if count == 50/self.Player.player_tank.fr:
                    send("FIRE")
                    count = 0
            count += 1
            if count >= 50/self.Player.player_tank.fr:
                count=50/self.Player.player_tank.fr

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
            data = self.conn.s.recvfrom(3000000)
            try:
                packet = pickle.loads(data[0])
                self.Player.Set_Coords(packet.x, packet.y)
                if not packet.bullets: pass
                else:
                    self.Player.player_tank.bullets = packet.bullets
                if not packet.others: continue
                for i in packet.others:
                    x = packet.others[i]["x"]
                    y = packet.others[i]["y"]
                    p = Player()
                    p.ID = i
                    p.Create_Tank((x,y,0,0,0,0,packet.others[i]["name"]))
                    p.player_tank.bullets = packet.others[i]["bullets"]
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
    def Create_Tank(self,Tank_INFO):
        self.player_tank = Tank(Tank_INFO[0],Tank_INFO[1],Tank_INFO[2],Tank_INFO[3],Tank_INFO[4],Tank_INFO[5],Tank_INFO[6])
        self.name = Tank_INFO[5]

    def Set_Coords(self,x,y):
        self.player_tank.x = x
        self.player_tank.y = y

    def Draw(self,screen,font,bot,top,bullettimage):
        self.player_tank.Draw(screen,font,bot,top,bullettimage)
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
        self.bullets = []
    def Draw(self,screen,font,bot,top,bullettimage):
        def rot_center(image, angle):
            """rotate an image while keeping its center and size"""
            orig_rect = image.get_rect()
            rot_image = pygame.transform.rotate(image, angle)
            rot_rect = orig_rect.copy()
            rot_rect.center = rot_image.get_rect().center
            rot_image = rot_image.subsurface(rot_rect).copy()
            return rot_image
        pos = pygame.mouse.get_pos()
        delta_x = (self.x - pos[0])
        delta_y = -(self.y - pos[1])
        self.angle = math.atan2(delta_y, delta_x)
        self.angle = math.degrees(self.angle)
        text = font.render(self.name, False, (0, 0, 0))
        spacing = text.get_rect().width / 2
        screen.blit(text,(self.x+12-spacing,self.y-20))

        screen.blit(bot,(self.x,self.y))

        screen.blit(rot_center(top,self.angle-90),(self.x,self.y))
        # pygame.draw.circle(screen, (0,0,0), (self.x + 10, self.y + 10), 10)
        if not self.bullets: pass
        else:
            for bullet in self.bullets:
                bullet.Draw(screen,bullettimage)

class Bullet(object):
    def __init__(self,x,y,tar_x,tar_y,speed):
        self.x = x
        self.y = y
        self.tar_x = tar_x
        self.tar_y = tar_y
        self.speed = speed
        self.active = True
    def Draw(self,screen):
        pygame.draw.rect(screen, (0, 0, 255), (int(round(self.x + 10)), int(round(self.y + 10))))

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
        submitbutton = pygame.Rect((325, 600, 150, 60))
        submitimage = pygame.image.load("res/Submit.png")
        while True:
            DISPLAYSURF.fill((0, 0, 0))

            events = pygame.event.get()
            for event in events:
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if submitbutton.collidepoint(mouse_pos):
                        if serverip == "":
                            return("83.128.201.15")
                        else:
                            print('button in ip chooser was pressed at {0}'.format(mouse_pos))
                            print(serverip)

                            return(serverip)
            ip.update(events)
            ip.draw(DISPLAYSURF)
            pygame.draw.rect(DISPLAYSURF, [255,255,255], line)
            DISPLAYSURF.blit(starttext, (252, 100))
            pygame.draw.rect(DISPLAYSURF, [0, 0, 0], submitbutton)
            DISPLAYSURF.blit(submitimage, (325, 600))
            # draw objects down here
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

class Creation(object):
    def random(self):
        b = random.randint(2, 18)
        a = random.randint(1, b - 1)
        c = random.randint(b + 1, 19)
        return [a, b - a, c - b, 20 - c]
    def drawtext(self, surf, text, size, x, y):
        myfont_name = pygame.font.match_font('MS Sans Serif')
        font = pygame.font.Font(myfont_name, size)
        text_surface = font.render(text, False, (255,255,255))
        text_rect = text_surface.get_rect()
        text_rect.topleft = (x,y)
        surf.blit(text_surface, text_rect)
    def __new__(cls):
        pygame.init()
        DISPLAYSURF = pygame.display.set_mode((800, 800))
        myfontlarge = pygame.font.SysFont('MS Sans Serif', 100)
        myfont = pygame.font.SysFont('MS Sans Serif', 75)
        # ---------Name------------
        name = myfontlarge.render('Name', False, (255,255,255))
        nameinput = eztext.Input(x=475, y= 0, maxlength=10, color=(255,255,255), font=pygame.font.Font(None, 100))
        # -----------Pool----------
        poolnum = 20
        pool = myfont.render('Pool: ', False, (255,255,255))
        # -----------Health----------
        healthnum = 1
        health = myfont.render('Health: ', False, (255, 255, 255))
        healthhoog = pygame.Rect((740, 200, 50, 50))
        healthlaag = pygame.Rect((680, 200, 50, 50))
        # -----------Speed----------
        speednum = 1
        speed = myfont.render('Speed: ', False, (255, 255, 255))
        speedhoog = pygame.Rect((740, 300, 50, 50))
        speedlaag = pygame.Rect((680, 300, 50, 50))
        # -----------Firerate----------
        fireratenum = 1
        firerate = myfont.render('Firerate: ', False, (255, 255, 255))
        firehoog = pygame.Rect((740, 400, 50, 50))
        firelaag = pygame.Rect((680, 400, 50, 50))
        # -----------Bulletdamage----------
        bulletdamagenum = 1
        bulletdamage = myfont.render('Bulletdamage: ', False, (255, 255, 255))
        bullethoog = pygame.Rect((740, 500, 50, 50))
        bulletlaag = pygame.Rect((680, 500, 50, 50))
        # -----------Submit----------
        submitbutton = pygame.Rect((150, 600, 150, 60))
        submitimage = pygame.image.load("res/Submit.png")
        # -----------Random----------
        randombutton = pygame.Rect((500, 600, 114, 114))
        randomimage = pygame.image.load("res/Random.png")
        while True:
            DISPLAYSURF.fill((0, 0, 0))
            events = pygame.event.get()
            if poolnum > 20:
                poolnum = 20
            if healthnum == 0:
                healthnum = 1
            if speednum == 0:
                speednum = 1
            if fireratenum == 0:
                fireratenum = 1
            if bulletdamagenum == 0:
                bulletdamagenum = 1
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if healthhoog.collidepoint(mouse_pos) and poolnum > 0:
                        if health == 1:
                            continue
                        else:
                            healthnum += 1
                            poolnum += -1
                    elif healthlaag.collidepoint(mouse_pos):
                        if healthnum == 1:
                            continue
                        else:
                            healthnum += -1
                            poolnum += 1
                    elif speedhoog.collidepoint(mouse_pos)and poolnum > 0:
                        speednum += 1
                        poolnum += -1
                    elif speedlaag.collidepoint(mouse_pos):
                        if speednum == 1:
                            continue
                        else:
                            speednum += -1
                            poolnum += 1
                    elif firehoog.collidepoint(mouse_pos)and poolnum > 0:
                        fireratenum += 1
                        poolnum += -1
                    elif firelaag.collidepoint(mouse_pos):
                        if fireratenum == 1:
                            continue
                        else:
                            fireratenum += -1
                            poolnum += 1
                    elif bullethoog.collidepoint(mouse_pos)and poolnum > 0:
                        bulletdamagenum += 1
                        poolnum += -1
                    elif bulletlaag.collidepoint(mouse_pos):
                        if bulletdamagenum == 1:
                            continue
                        else:
                            bulletdamagenum += -1
                            poolnum += 1
                    elif submitbutton.collidepoint(mouse_pos) and poolnum == 0:
                        print("Informatie {} \nHealth: {}\nSpeed: {}\nFirerate: {} \nBullet Damage: {}".format(nameinput.value, healthnum,speednum,fireratenum,bulletdamagenum))
                        pygame.mixer.music.stop()
                        return(0,0,healthnum,speednum,fireratenum,bulletdamagenum,nameinput.value)
                    elif randombutton.collidepoint(mouse_pos):
                        stats = (cls.random(cls))
                        poolnum = 0
                        healthnum = 1 + stats[0]
                        speednum = 1 + stats[1]
                        fireratenum = 1+ stats[2]
                        bulletdamagenum = 1 + stats[3]

            nameinput.update(events)
            nameinput.draw(DISPLAYSURF)
            DISPLAYSURF.blit(name, (0,0))
            DISPLAYSURF.blit(pool, (0,100))
            cls.drawtext(cls, DISPLAYSURF, str(poolnum), 75, 140, 100)
            cls.drawtext(cls, DISPLAYSURF, str(healthnum), 75, 190, 200)
            cls.drawtext(cls, DISPLAYSURF, str(speednum), 75, 180, 300)
            cls.drawtext(cls, DISPLAYSURF, str(fireratenum), 75, 220, 400)
            cls.drawtext(cls, DISPLAYSURF, str(bulletdamagenum), 75, 370, 500)

            DISPLAYSURF.blit(health, (0, 200))
            DISPLAYSURF.blit(speed, (0, 300))
            DISPLAYSURF.blit(firerate, (0, 400))
            DISPLAYSURF.blit(bulletdamage, (0, 500))

            pygame.draw.rect(DISPLAYSURF, [0, 255, 0], healthhoog)
            pygame.draw.rect(DISPLAYSURF, [255, 0, 0], healthlaag)

            pygame.draw.rect(DISPLAYSURF, [0, 255, 0], speedhoog)
            pygame.draw.rect(DISPLAYSURF, [255, 0, 0], speedlaag)

            pygame.draw.rect(DISPLAYSURF, [0, 255, 0], firehoog)
            pygame.draw.rect(DISPLAYSURF, [255, 0, 0], firelaag)

            pygame.draw.rect(DISPLAYSURF, [0, 255, 0], bullethoog)
            pygame.draw.rect(DISPLAYSURF, [255, 0, 0], bulletlaag)

            pygame.draw.rect(DISPLAYSURF, [0, 0, 0], submitbutton)
            pygame.draw.rect(DISPLAYSURF, [0, 0, 0], randombutton)

            DISPLAYSURF.blit(submitimage, (150, 600))
            DISPLAYSURF.blit(randomimage, (500, 600))
            pygame.display.update()
