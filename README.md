forseti2
========

forseti2 (named after the Norse god of justice) is the field control software for the Pioneers in Engineering 2014 Robotics Competition. 

## Installation on Ubuntu Linux ##

forseti2 is depdendent on several external libraries. Follow these instructions on Debian/Ubuntu Linux to install these dependencies. On other platforms, you will need to determine how to install these dependencies. 

### LCM ####

Refer to the LCM install instructions at [lcm.googlecode.com wiki](https://code.google.com/p/lcm/wiki/BuildInstructions). 

Once LCM is built, move `lcm-1.0.0/lcm-java/lcm.jar` into this directory to take advantage of `lcm-spy.sh` packet introspection.

### OpenCV ###
You don't actually need OpenCV. 

### pygame ###

    $ sudo apt-get install python-pygame
    
### arduino ###
    $ sudo apt-get install arduino
    
### pyfirmata ###
    $ sudo pip install pyfirmata

## Installation on Mac OS X ##

On OS X, we use MacPorts to obtain the requisite libaries for at least part of the stack. 

forseti2 is depdendent on several external libraries. Follow these instructions on OS X to install these dependencies. 

### python ###

OS X comes with its own distribution of python. However, you should install the MacPorts distribution to be able to easily install external libraries on top of python. 

    $ sudo port install python27
    $ sudo port install py27-pip
    $ sudo port select --set python python27

### Flask ###

    $ sudo pip install flask

### LCM ####

Refer to the LCM install instructions at [lcm.googlecode.com wiki](https://code.google.com/p/lcm/wiki/BuildInstructions). 

Once LCM is built, move `lcm-1.0.0/lcm-java/lcm.jar` into this directory to take advantage of `lcm-spy.sh` packet introspection.

### pygame ###
    $ sudo port install py27-game
    
### arduino and firmata ###

There's no port avaialble for arduino or firmata. 

## Nodes and their Functions ##

### timer.py ###

Maintains match timer and current match stage.

Inputs:

- Timer/Control: TimeControl
  + receives commands for the match timer (start, pause, reset)

Outputs:

- Timer/Time: Time
  + publishes (every .3 secs) time elapsed in current match and stage, as well as the current stage name

### lcm_ws_bridge.py ###

Bridges lcm to websockets so javascript applications can access the network

Inputs:

- *: *
  + receives whatever the websocket clients request

Outputs:

- *: *
  + publishes whatever the websocket clients request

### robot_controller.py ###

Maintains state of each robot

Inputs:

- Timer/Time: Time
  + uses current match stage to determine robot stage unless overridden or emergency stopped
- Robot[0-3]/Estop: Estop
  + uses current emergency stop state and overrides all robot state if in estop mode
- Robot[0-3]/Override: Override
  + determines whether or not robot is in manual override mode (overrides timers only)
- Robot[0-3]/RobotState: RobotState
  + controls robot state using manual override only if in override mode

Outputs:

- Robot[0-3]/RobotControl: RobotControl
  + publishes (every .3 secs) the state of the robot (estop?, autonomous?, enabled?)

### heartbeat.py ###

Acts as a heartbeat for clients to confirm they are connected to the field network

Inputs:


Outputs:

- Heartbeat/Beat: Heartbeat
  + oscillates between True and False every second

