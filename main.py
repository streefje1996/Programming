import pygame, sys
import Classes
from pygame.locals import *


#Init the pygame module
pygame.init()

mainplayer = Classes.Player("streefje")


#create screen and set Title
DISPLAYSURF = pygame.display.set_mode((800,800))
pygame.display.set_caption("Tank Battle")

level = Classes.Level()
level.load_file()
tiletable = level.load_tile_table("res/terrain.png",32,32)

server = Classes.Serverconn("83.128.201.15",mainplayer)

Sending_Thread = Classes.SendThread(0, mainplayer,server)
Recving_Thread = Classes.RecvThread(0,mainplayer,server)
Sending_Thread.start()
Recving_Thread.start()


while True:
    #check for exit
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    level.Draw_Level(tiletable,DISPLAYSURF)
    mainplayer.Draw(DISPLAYSURF)
    try:
        for player in Recving_Thread.others:
            Recving_Thread.others[player].Draw(DISPLAYSURF)
    except:
        pass




    #Update screen
    pygame.display.update()