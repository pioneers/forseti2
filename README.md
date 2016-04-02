forseti2
========

## to deploy a driver station: `

wget https://raw.githubusercontent.com/karthik-shanmugam/forseti2/2016/driver_station.sh; chmod +x driver_station.sh; ./driver_station`

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

Maintains match state (timer and robot states)

Inputs:

- Match/Init : Match
  + resets match timer when a new match is initialized
- Timer/Control: TimeControl
  + receives commands for the match timer (start, pause, reset)
- Robot[0-3]/Estop: Estop
  + uses current emergency stop state and overrides all robot state if in estop mode
- Robot[0-3]/Override: Override
  + determines whether or not robot is in manual override mode (overrides timers for manual operation)
- Robot[0-3]/RobotState: RobotState
  + sets robot state using manual override only if in override mode

Outputs:

- Timer/Time: Time
  + publishes (every .3 secs) time elapsed in current match and stage, as well as the current stage name
- Robot[0-3]/RobotControl: RobotControl
  + publishes (every .3 secs) the state of the robot (estop?, autonomous?, enabled?)

### lcm_ws_bridge.py ###

TODO:

- Optimization/stress testing
- Packet sniffer for testing

Bridges lcm to websockets so javascript applications can access the network

Inputs:

- *: *
  + receives whatever the websocket clients request

Outputs:

- *: *
  + publishes whatever the websocket clients request

### GameObjectTimer.py ###

A timer for the buttons on the field

TODO:

- Publish which button triggered the timer
- Help field_control.py identify when to spin motors (maybe generate a uid for each unique run of the timer)

Inputs:

- Game_Button[0-1]/Button: Button
  + uses button status to trigger the timer
- Timer/Time: Time
  + only triggers on button presses during teleop and autonomous phases of a match

Outputs:

- GameObjectTimer/LighthouseTime: LighthouseTime
  + publishes (every .3 secs) the state of the timer
  + describes which button triggered the timer and how much time is left, or that the buttons are available

### field_control.py ###

Manages electronics on the field

TODO:

- Business logic regarding only spinning the motor once per button press and avoiding race conditions (maybe the timer can send UIDs?)
- Actual interfacing with hardware

Inputs:

- GameObjectTimer/LighthouseTime: LighthouseTime
  + uses timer info to determine when to dump balls onto field
- Timer/Time: Time
  + only dumps balls onto field during teleop and autonomous phases

Outputs:

- Game_Button[0-1]/Button: Button
  + publishes (every .3 secs) the state of a button
- Game_Motor[0-1]/Motor: Motor
  + publishes (every .3 secs) the state of a motor

Notes:

- There may be multiple instances of this node, each controlling a different field element
- There may be other things to add to the field later, such as status lights.

### heartbeat.py ###

Acts as a heartbeat for clients to confirm they are connected to the field network

Inputs:


Outputs:

- Heartbeat/Beat: Heartbeat
  + oscillates between True and False every second


## Functions of Modified Dawn ##

### Set Robot State ###

- Listen to a specific Robot[0-3]/RobotControl channel and sends messages to robot accordingly
- TODO: Set team flags on robot

### Connect to Correct Robot Automatically ###

- Either receive the correct robot IP from the field or configure so each driver station corresponds to a static robot ip
- Give meaningful feedback to field and students about robot connection status

### Display Information from Field ###

- Match state and timer
- Lighthouse availability and timer
- Team's robot state
- If other team's robots were manually disabled/estopped?
- Which motor on the field is spinning
- Video feed from field
- Heartbeat

### Publish Information to Field

- Connection status of robot

### Disable Dawn Features

- Text editor and upload/run functionality
- Stop button should always be enabled

### Communication with field operators? (help button / chat)

## UI nodes ##

### TODO: ALL OF THESE!!! (Except Network Monitor) ###

### Network Monitor ###

- Displays live plots of messages/second on each channel

### Judge Console ###

- Allow score input for current match
- Display field info like Dawn?

### Field Console ###

- View robot states and allow for manual overriding and estop
- Allow control of match timer and robot enumeration (telling dawn to connect to robots)

### Stream Overlay ###

- Display field info (like dawn), scores, and upcoming matches

### Audience UI ###

- Like the stream overlay but as standalone webpage

## Status Light Behavior ##

### Lighthouse Chief Lights ##

- All lights normally off
- Red light on when button is currently pressed
- Green light flashes for 3s when button triggers a lighthouse chief
- Yellow light on when lighthouse on cooldown

