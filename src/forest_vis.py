#!/usr/bin/env python2.7

"""
This node visualizes what the field dispensers should be doing.
"""

import lcm
import forseti2 as fs2
import pygame
import time
import math
import threading
import settings

TEAM_BLUE = 0
TEAM_GOLD = 1
STATE_HELD = 2
STATE_RELEASED = 3

WIDTH=640
HEIGHT=480
DSIZE=50
class DispenserDisplay:
    def __init__(self, team, lcm, window):
        self.team = team
        self.lcm = lcm
        self.window = window
        self.debug = True
        self.state = {TEAM_GOLD:(0,0,0,0),
                      TEAM_BLUE:(0,0,0,0)}


        self.coords = {
        TEAM_BLUE:
        [(WIDTH-DSIZE, 50),
        (WIDTH-DSIZE, 150),
        (WIDTH-DSIZE, 250),
        (WIDTH-DSIZE, 350)],
        TEAM_GOLD:
        [(0, 350),
        (0, 250),
        (0, 150),
        (0, 50)],
        }

        self.team_name = {TEAM_BLUE:'B',
                         TEAM_GOLD:'G'}

        self.colors = {0:(127, 127, 127),
                      STATE_HELD:(255,0,0),
                      STATE_RELEASED:(0,255,0)}

        self._read_thread = threading.Thread(target=self._read_loop)
        self._read_thread.daemon = True
        self._draw_thread = threading.Thread(target=self._draw_loop)
        self._draw_thread.daemon = True

        self.myfont = pygame.font.SysFont("calibri", 36, bold=True)

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
                # TODO: visualize msg.lights[b][c]
                pass
            activated = STATE_HELD if (msg.servos[b] == settings.SERVO_HELD) else STATE_RELEASED
            team = b / 4
            dispenser = b % 4
            v = list(self.state[team])
            v[dispenser] = activated
            self.state[team] = v

    def _draw(self):
        self.window.fill((255,255,255))
        pygame.draw.rect(self.window, (255, 255, 200), (0, 0, 320, 480))
        pygame.draw.rect(self.window, (200, 200, 255), (320, 0, 320, 480))
        for team in (TEAM_GOLD, TEAM_BLUE):
            for i in range(4):
                coords = self.coords[team][i]
                rect = (coords[0], coords[1], 50, 50)
                color = self.colors[self.state[team][i]]
                pygame.draw.rect(self.window, color, rect)
                txt = str(i)
                tcoords = [coords[x] + 15 for x in range(2)]
                # print tcoords
                self._draw_text(txt, tcoords, (0,0,0))


if __name__ == '__main__':
    try:
        WIDTH, HEIGHT = (640, 480)
        pygame.init()
        window = pygame.display.set_mode((WIDTH, HEIGHT))

        lc = lcm.LCM(settings.LCM_URI)
        dd = DispenserDisplay(TEAM_GOLD,
            lc,
            window)
        sub = lc.subscribe("/forest/cmd", dd._forest_cmd_handler)
        dd.start()
        while True:
            time.sleep(.1)

    except KeyboardInterrupt:
        raise
    except :
        raise

