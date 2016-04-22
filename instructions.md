1. cd forseti2;tmux;./run_nodes.sh
2. in the terminal that echoed "for status_lights_driver" run `sudo python status_lights_driver.py /dev/$RAINY_ARDUINO_PATH`
3. in the terminal that echoed "for buttons" run `sudo python field_control.py -b 0 /dev/$BUTTON_0_ARDUINO_PATH -b 1 /dev/$BUTTON_1_ARDUINO_PATH -s /dev/$SHOOTER_ARDUINO_PATH`
4. go to pioneers.github.io/forseti2 to run matches
