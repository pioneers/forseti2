forseti2
========

forseti2 (named after the Norse god of justice) is the field control software for the Pioneers in Engineering 2014 Robotics Competition. 

## Installation ##

forseti2 is depdendent on several external libraries. Follow these instructions on Debian/Ubuntu Linux to install these dependencies. On other platforms, you will need to determine how to install these dependencies. 

### LCM ####

Refer to the LCM install instructions at [lcm.googlecode.com wiki](https://code.google.com/p/lcm/wiki/BuildInstructions). 

Once LCM is built, move `lcm-1.0.0/lcm-java/lcm.jar` into this directory to take advantage of `lcm-spy.sh` packet introspection.

### OpenCV ###
In the terminal, execute:
    
    $ sudo apt-get install python-opencv

### pygame ###

    $ sudo apt-get install python-pygame
