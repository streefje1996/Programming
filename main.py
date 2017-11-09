import pygame, sys
import Classes
from pygame.locals import *

#----------CONNCT TO IP------------
#"83.128.201.15"
#----------------------------------

#Init the pygame module
pygame.init()
pygame.font.init()
myfont = pygame.font.SysFont('Comic Sans MS', 15)

mainplayer = Classes.Player("Streefje")
mainplayer.Create_Tank(0,0,1,2,3,4)

icon = pygame.image.load("res/pp.png")

#create screen and set Title
DISPLAYSURF = pygame.display.set_mode((800,800))
pygame.display.set_caption("Tank Battle")
pygame.display.set_icon(icon)

level = Classes.Level()
level_overlay = Classes.Level()
level_overlay.load_file("extra_map.map")
level.load_file()
tiletable = level.load_tile_table("res/terrain.png",32,32)

server = Classes.Serverconn(Classes.Intro(),mainplayer)

Sending_Thread = Classes.SendThread(0, mainplayer,server)
Recving_Thread = Classes.RecvThread(0,mainplayer,server)
Sending_Thread.start()
Recving_Thread.start()
Classes.Music()

while True:
    pygame.time.Clock().tick(60)
    #check for exit
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    level.Draw_Level(tiletable,DISPLAYSURF)
    level_overlay.Draw_Level(tiletable,DISPLAYSURF)
    mainplayer.Draw(DISPLAYSURF,myfont)
    try:
        for player in Recving_Thread.others:
            Recving_Thread.others[player].Draw(DISPLAYSURF,myfont)
    except:
        pass

    #Update screen
    pygame.display.update()