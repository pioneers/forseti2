forseti2
========
forseti2 (Named after the Norse god of justice) is PiE's third* iteration of a Field Control software. It has been in use from 2014-2017, with substantial changes along the way.

## Deploying Driver Stations
Driver Stations can be downloaded from PieCentral's [Releases section](https://github.com/pioneers/PieCentral/releases), or built locally using the `dawn/fieldcontrol` branch.

### Installing for MacOS and GNU/Linux
 1. Download the `darwin-x64` or `linux-x64` release anywhere (preferably desktop)
 2. In Terminal, run `driver_station.sh`
 3. Run Field Control Dawn

### Installing for Windows
 1. Download the `win32-ia32` release anywhere
 2. On the Desktop:
   * Create the file `bridge_address.txt` and write the Controller's IP address
   * Create the file `station_number.txt` and write the station number you want to be (0, 1, 2, 3 => blue1, blue2, gold1, gold2)
 3. Run Field Control Dawn

## Deploying Field Controller
forseti2 is dependent on external libraries, so there will be some OS-dependent instructions.

### [Lightweight Communications and Marshalling (LCM)](https://lcm-proj.github.io/)
1. Follow Online instructions on how to build it on your system.
2. Once LCM is built, move `lcm.jar` into the forseti2 directory to take advantage of `lcm-spy.sh` packet introspection.

### Installing for Ubuntu and MacOS
1. Install LCM as detailed above
2. If Ubuntu, also run:
```bash
sudo apt-get install arduino;
sudo pip install pyfirmata;
```

## Nodes
### timer.py
Maintains match state (timer and robot states)

#### Inputs
* Match/Init: Match
  * Resets match timer when a new match is initialized
* Timer/Control: TimeControl
  * Receives commands for the match timer (start, pause, reset)
* Robot[0-3]/Estop: Estop
  * Uses current emergency stop state and overrides all robot state if in estop mode
* Robot[0-3]/Override: Override
  * Determines whether or not robot is in manual override mode (overrides timers for manual operation)
* Robot[0-3]/RobotState: RobotState
  * Sets robot state using manual override only if in override mode

#### Outputs
* Timer/Time: Time
  * Publishes (every .3 secs) time elapsed in current match and stage, as well as the current stage name
* Robot[0-3]/RobotControl: RobotControl
  * Publishes (every .3 secs) the state of the robot (estop?, autonomous?, enabled?)

### lcm_ws_bridge.py
Bridges LCM to Websockets so JavaScript applications can access the network

### field_control.py
Manages electronics on the field

#### Inputs
* GameObjectTimer/LighthouseTime: LighthouseTime
  * Uses timer info to determine when to dump balls onto field
* Timer/Time: Time
  * Only dumps balls onto field during teleop and autonomous phases

#### Outputs
* Game_Button[0-1]/Button: Button
  * Publishes (every .3 secs) the state of a button
* Game_Motor[0-1]/Motor: Motor
  * Publishes (every .3 secs) the state of a motor

### heartbeat.py
Heartbeat for clients to confirm they are connected to the field network

#### Outputs
* Heartbeat/Beat: Heartbeat
  * Oscillates between True and False every second?

## Modifications to Dawn
* Listens to a specific Robot[0-3]/RobotControl channel and sends messages to robot accordingly
* Give meaningful feedback to field and students about robot connection status
* Display Field Information
  * Match state and timer
  * Heartbeat
* Manual start disabled in match

## Field Controller Information
### Network Monitor
* Displays live plots of messages/second on each channel

### Judge Console
* Allow score input for current match

### Field Console
* View robot states and allow for manual overriding and estop
* Allow control of match timer and robot enumeration (telling dawn to connect to robots)

### Stream Overlay
* Display field info (like dawn), scores, and upcoming matches

### Audience UI
* Like the stream overlay but as standalone webpage

