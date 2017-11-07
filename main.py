import pygame, sys
import Classes
from pygame.locals import *

#Init the pygame module
pygame.init()

#create screen and set Title
DISPLAYSURF = pygame.display.set_mode((460,120))
pygame.display.set_caption("Tank Battle")

level = Classes.Level()
level.load_file()
while True:
    #check for exit
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    pygame.draw.rect(DISPLAYSURF, (0,255,0), (100,50,20,20))


    #Update screen
    pygame.display.update()