"""
xbox_driver.py

@author: Allen Li
"""

import lcm
import time
import pygame
import sys
import forseti2 as fs2
import settings

CHANNEL_NAME = "xbox0/state"
SLEEP_TIME = 0.01

lc = lcm.LCM(settings.LCM_URI)

msg = fs2.xbox_controller()
msg.header = fs2.header()
msg.header.seq = 0

pygame.joystick.init()
if pygame.joystick.get_count() == 0:
    print "Can't find controller..."
    sys.exit(1)
else:
    pygame.init()
    j = pygame.joystick.Joystick(0)
    j.init()
    num_axes = j.get_numaxes()
    num_buttons = j.get_numbuttons()

def send_msg(m):
    m.header.seq += 1
    m.header.time = time.time()
    print('fs2.xbox_driver:')
    print('    header.seq=' + str(m.header.seq))
    print('    header.time=' + str(m.header.time))
    print('    axes=' + str(m.axes))
    print('    buttons=' + str(m.buttons))
    lc.publish(CHANNEL_NAME, m.encode())

def set_controller_status(m):
    if not j.get_init():
        print "Joystick not initialized..."
        sys.exit(1)
    pygame.event.pump()
    m.axes = [j.get_axis(i) for i in xrange(num_axes)]
    m.buttons = [j.get_button(i) for i in xrange(num_buttons)][-11:] # only get 11 control inputs

def main():
    while True:
        set_controller_status(msg)
        time.sleep(SLEEP_TIME)
        send_msg(msg)

if __name__ == '__main__':
    main()
