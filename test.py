import pygame, sys
import eztext
from pygame.locals import *

pygame.init()
pygame.font.init() #Voor de tekst op de knopjes
DISPLAYSURF = pygame.display.set_mode((800,800))
pygame.display.set_caption("Tank Battle")

serverip = ""

class Intro:
    def ipchooser(self):
        startbuttonpos = (300, 360, 200, 80)
        startbutton = pygame.Rect(startbuttonpos)
        ip = eztext.Input(maxlength=45, color=(255, 255, 255), prompt='Type ip of server here: ')
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
                        print(chosenip)
            ip.update(events)
            ip.draw(DISPLAYSURF)
            # pygame.display.flip()
            myfont = pygame.font.SysFont('MS Sans Serif', 50)
            pygame.draw.rect(DISPLAYSURF, [0, 255, 0], startbutton)  # draw objects down here
            starttext= myfont.render('Submit', False, (0, 0, 0))
            DISPLAYSURF.blit(starttext, (300, 370))
            pygame.display.update()
            chosenip = ip.value
    def __init__(self):
        myfont = pygame.font.SysFont('MS Sans Serif', 90)
        startbuttonpos = (300, 360, 200, 80)
        startbutton = pygame.Rect(startbuttonpos)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if startbutton.collidepoint(mouse_pos):
                        print('button was pressed at {0}'.format(mouse_pos))
                        self.ipchooser()
            pygame.draw.rect(DISPLAYSURF, [0, 255, 0], startbutton)  # draw objects down here
            starttext= myfont.render('START', False, (0, 0, 0))
            DISPLAYSURF.blit(starttext, (300, 370))
            pygame.display.update()

Intro()