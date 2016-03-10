import lcm
import forseti2
import settings
import LCMNode






lc = lcm.LCM(settings.LCM_URI)

button = forseti2.Button()
button.pressed = True


while True:
    raw_input("press enter to press the button")
    lc.publish("Game_Button/Button", button.encode())




