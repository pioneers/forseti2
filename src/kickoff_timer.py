# -*- coding: utf-8 -*-
"""
Created on Thu Feb  20 01:34:13 2014

@author: ajc

countdown to kickoff.
"""

import pygame
import datetime
import time

def draw_text(surface, font, text, pos, color):
    label = font.render(text, 1, color)
    surface.blit(label, pos)

def main():

    pygame.init()
    window = pygame.display.set_mode((1280, 1024), pygame.FULLSCREEN)

#    window = pygame.display.set_mode((1280, 1024))
    pygame.mouse.set_visible(False)
    headerfont = pygame.font.SysFont("freesans", 100)
    font = pygame.font.SysFont("freesans", 250)

    kickoff = datetime.datetime(2014, 3, 1, 9, 0, 0)
    while True:
        window.fill((0,0,0))
        now = kickoff - datetime.datetime.now()
        days = now.days

        hours = now.seconds / 3600
        minutes = (now.seconds %3600)/ 60
        seconds = now.seconds % 60
        daytxt="{0} days".format(str(days).zfill(2))
        strt="{0}:{1}:{2}".format(str(hours).zfill(2),
            				str(minutes).zfill(2),
            				str(seconds).zfill(2))
        draw_text(window, font, daytxt, (100, 200), (255,255,255))
        draw_text(window, font, strt, (100, 400), (255,255,255))
        draw_text(window, headerfont, "Countdown to Kickoff 2014!!! ", (10, 10), (255,255,255))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key ==  pygame.K_ESCAPE:
                return
        time.sleep(.01)

if __name__ == '__main__':
    main()
