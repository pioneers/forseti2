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

CHANNEL_PREFIX = "xbox/state"
SLEEP_TIME = 0.01

OSX = 0
LINUX = 1
def determine_platform(joystick):
    if joystick.get_numbuttons() == 15:
        return OSX
    else:
        return LINUX

def send_msg(m, joy_num = 0):
    m.header.seq += 1
    m.header.time = time.time()
    channel = CHANNEL_PREFIX + '/' + node_name + '/' + str(joy_num)
    print('fs2.xbox_driver:')
    print('    channel=' + channel)
    print('    header.seq=' + str(m.header.seq))
    print('    header.time=' + str(m.header.time))
    print('    axes=' + str(m.axes))
    print('    buttons=' + str(m.buttons))
    lc.publish(channel, m.encode())

# Sets the controller status, and returns True if
# updated buttons, False otherwise. 
def set_controller_status(m, j):
    if not j.get_init():
        print "Joystick not initialized..."
        sys.exit(1)
    if platform == OSX: # compatability with Mac OS X Xbox Controller Drivers
        axes = [j.get_axis(i) for i in xrange(num_axes)]
        buttons = [j.get_button(i) for i in (11, 12, 13, 14, 8, 9, 5, 4, 10, 6, 7)]
    else: # We'll assume you're on Ubuntu. 
        axes = [j.get_axis(i) for i in xrange(num_axes)]
        buttons = [j.get_button(i) for i in xrange(num_buttons)]
    ans = axes != m.axes # whether there's been a change
    m.axes = axes
    m.buttons = buttons
    return ans

def main():
    global lc
    global node_name
    global joysticks
    global messages
    global platform
    global num_axes
    global num_buttons
    global num_joysticks

    lc = lcm.LCM(settings.LCM_URI)

    if len(sys.argv) > 1:
        node_name = sys.argv[1]
    else:
        node_name = "default"

    pygame.init()
    if pygame.joystick.get_count() == 0:
        print "Can't find controller..."
        sys.exit(1)
    num_joysticks = pygame.joystick.get_count()

    messages = [fs2.xbox_joystick_state() for i in xrange(num_joysticks)]
    for msg in messages:
        msg.header = fs2.header()
        msg.header.seq = 0

    joysticks = [pygame.joystick.Joystick(i) for i in xrange(num_joysticks)]
    for j in joysticks:
        j.init()

    platform = determine_platform(joysticks[0])
    num_axes = joysticks[0].get_numaxes()
    num_buttons = joysticks[0].get_numbuttons()

    while True:
        time.sleep(SLEEP_TIME)
        pygame.event.pump() # must pump for more info from pygame
        for j, msg in zip(joysticks, messages):
            if set_controller_status(msg, j):
                send_msg(msg, j.get_id())

if __name__ == '__main__':
    main()
