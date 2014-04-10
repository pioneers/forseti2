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

OSX = 0
LINUX = 1
def determine_platform(joystick):
    if joystick.get_numbuttons() == 15:
        return OSX
    else:
        return LINUX

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
    pygame.event.pump() # must pump for more info from pygame
    if platform == OSX: # compatability with Mac OS X Xbox Controller Drivers
        m.axes = [j.get_axis(i) for i in xrange(num_axes)]
        m.buttons = [j.get_button(i) for i in (11, 12, 13, 14, 8, 9, 5, 4, 10, 6, 7)]
    else: # We'll assume you're on Ubuntu. 
        m.axes = [j.get_axis(i) for i in xrange(num_axes)]
        m.buttons = [j.get_button(i) for i in xrange(num_buttons)]

def main():
    global lc
    global j
    global platform
    global num_axes
    global num_buttons

    lc = lcm.LCM(settings.LCM_URI)

    msg = fs2.xbox_joystick_state()
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
        platform = determine_platform(j)
        num_axes = j.get_numaxes()
        num_buttons = j.get_numbuttons()
    while True:
        time.sleep(SLEEP_TIME)
        set_controller_status(msg)
        send_msg(msg)

if __name__ == '__main__':
    main()
