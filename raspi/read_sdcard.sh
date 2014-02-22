#!/bin/bash
#
# read_sdcard.sh
#
# reads the sdcard to a local disk image.
# via http://askubuntu.com/questions/227924/sd-card-clone-using-dd-command

sudo dd if=/dev/mmcblk0 of=sdimage.img