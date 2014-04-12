#!/usr/bin/env python2.7
"""
This node simulates a robot sending field commands.
"""
import sys
import lcm
import time
import forseti2 as fs2
import settings
import util

print 'starting piemos_field_cmd_test'

lc = lcm.LCM(settings.LCM_URI)
blue_seq = util.LCMSequence(lc, fs2.piemos_field_cmd, "piemos0/field_cmd")
gold_seq = util.LCMSequence(lc, fs2.piemos_field_cmd, "piemos3/field_cmd")

blue_keys = [
             dict(isFlash=False, isStart=False, isLeft=False, rfid_uid=199),
             dict(isFlash=True, isStart=True, isLeft=False, rfid_uid=200),
             dict(isFlash=True, isStart=True, isLeft=False, rfid_uid=201),
             dict(isFlash=True, isStart=True, isLeft=False, rfid_uid=202),
             dict(isFlash=True, isStart=False, isLeft=False, rfid_uid=200),
             dict(isFlash=True, isStart=False, isLeft=False, rfid_uid=201),
             dict(isFlash=True, isStart=False, isLeft=False, rfid_uid=202),
             dict(isFlash=False, isStart=False, isLeft=False, rfid_uid=200),
             dict(isFlash=False, isStart=False, isLeft=False, rfid_uid=201),
             dict(isFlash=False, isStart=False, isLeft=False, rfid_uid=202),
             ]

gold_keys = []


sleep_time = 2

while True:
    for key in blue_keys:
        blue_seq.publish(**key)
        time.sleep(sleep_time)
    for key in gold_keys:
        gold_seq.publish(**key)
        time.sleep(sleep_time)
