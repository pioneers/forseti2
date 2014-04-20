#!/usr/bin/env python2.7

"""
This node visualizes what the field dispensers should be doing.
"""

import lcm
import forseti2 as fs2
import pygame
import time
import threading
import settings

SERVO_RELEASED = False
RED = 0
YELLOW = 1
GREEN = 2
SERVO = 3

WIDTH=640
HEIGHT=480
DSIZE=80
SSIZE=40
class DispenserDisplay:
    def __init__(self, lcm, window):
        self.lcm = lcm
        self.window = window
        self.debug = True
        # state[dispenser_num] = [red, yellow, green, servo]
        self.state = {0: [0,0,0,0],
                      1: [0,0,0,0],
                      2: [0,0,0,0],
                      3: [0,0,0,0],
                      4: [0,0,0,0],
                      5: [0,0,0,0],
                      6: [0,0,0,0],
                      7: [0,0,0,0]}

        self.coords = [((WIDTH / 4) - (DSIZE / 2) + 20, 0),
                      (0, (HEIGHT / 4) - (DSIZE / 2)),
                      (0, (.75 * HEIGHT) - (DSIZE / 2)),
                      ((WIDTH / 4) - (DSIZE / 2) + 20, HEIGHT - DSIZE),
                      ((.75 * WIDTH) - (DSIZE / 2) - 20, HEIGHT - DSIZE),
                      (WIDTH - DSIZE, (HEIGHT / 4) - (DSIZE / 2)),
                      (WIDTH - DSIZE, (.75 * HEIGHT) - (DSIZE / 2)),
                      ((.75 * WIDTH) - (DSIZE / 2) - 20, 0)]

        self.colors = {0:(51,0,0),
                       1:(255,0,0),
                       2:(0,51,0),
                       3:(0,255,0),
                       4:(51,51,0),
                       5:(255,255,0),
                       6:(0,0,51),
                       7:(0,0,255)}

        self._read_thread = threading.Thread(target=self._read_loop)
        self._read_thread.daemon = True
        self._draw_thread = threading.Thread(target=self._draw_loop)
        self._draw_thread.daemon = True

        self.myfont = pygame.font.SysFont("calibri", 40, bold=True)

    def _draw_text(self, text, pos, color):
        label = self.myfont.render(text, 1, color)
        self.window.blit(label, pos)

    def _read_loop(self):
        while True:
            self.lcm.handle()

    def _draw_loop(self):
        while True:
            pygame.display.flip()
            self._draw()
            time.sleep(1.0/60)

    def start(self):
        self._read_thread.start()
        self._draw_thread.start()

    def _forest_cmd_handler(self, channel, data):
        msg = fs2.forest_cmd.decode(data)
        if self.debug:
            print("Received message on channel \"%s\"" % channel)
            print("   header.seq   = %s" % str(msg.header.seq))
            print("   header.time   = %s" % str(msg.header.time))
            print("   lights   = %s" % str(msg.lights))
            print("   servos   = %s" % str(msg.servos))
        for b in range(8):
            for c in range (3):
                self.state[b][c] = msg.lights[b][c]

            v = list(self.state[b])
            v[SERVO] = msg.servos[b] == settings.SERVO_RELEASED
            self.state[b] = v

    def _draw(self):
        self.window.fill((255,255,255))
        pygame.draw.rect(self.window, (200, 200, 255), (0, 0, 320, 480))
        pygame.draw.rect(self.window, (255, 255, 200), (320, 0, 320, 480))
        for dispenser in range(8):
            x, y = self.coords[dispenser]
            redrect = (x, y, SSIZE, SSIZE)
            color = self.colors[self.state[dispenser][RED]]
            pygame.draw.rect(self.window, color, redrect)

            yellowrect = (x + SSIZE, y, SSIZE, SSIZE)
            color = self.colors[self.state[dispenser][YELLOW] + 4]
            pygame.draw.rect(self.window, color, yellowrect)

            greenrect = (x, y + SSIZE, SSIZE, SSIZE)
            color = self.colors[self.state[dispenser][GREEN] + 2]
            pygame.draw.rect(self.window, color, greenrect)

            servorect = (x + SSIZE, y + SSIZE, SSIZE, SSIZE)
            color = self.colors[self.state[dispenser][SERVO] + 6]
            pygame.draw.rect(self.window, color, servorect)

            txt = str(dispenser)
            tcoords = (x + 15, y + 5)
            # print tcoords
            self._draw_text(txt, tcoords, (255,255,255))

if __name__ == '__main__':
    try:
        WIDTH, HEIGHT = (640, 480)
        pygame.init()
        window = pygame.display.set_mode((WIDTH, HEIGHT))

        lc = lcm.LCM(settings.LCM_URI)
        dd = DispenserDisplay(lc, window)
        sub = lc.subscribe("/forest/cmd", dd._forest_cmd_handler)
        dd.start()
        while True:
            time.sleep(.1)

    except KeyboardInterrupt:
        raise
    except :
        raise

