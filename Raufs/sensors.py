from sense_hat import SenseHat
from time import sleep
import threading

sense = SenseHat()

class CO2(threading.Thread):

        orange = [254, 110, 0]
        cyan = [0, 255, 255]
        co2_ppm = 500   # Good CO2 ppm

        # Gets current CO2 ppm reading
        def get_reading(self):
                return self.co2_ppm

        # Since I do not have CO2 sensor, joystick controlls the ppm measure.
        # If up is pressed, ppm becomes 8000, if down - 500.
        def monitor_joystick(self):
                while True:
                        event = sense.stick.wait_for_event()
                        
                        # Check if the joystick was pressed
                        if event.action == "pressed":
                                sense.clear()
                                
                                # Check which direction
                                if event.direction == "up":
                                        self.co2_ppm = 8000                                     # High CO2 ppm - fire present 
                                        sense.show_message("Fire", text_colour=self.orange)     # Up arrow
                                elif event.direction == "down":
                                        self.co2_ppm = 500
                                        sense.show_message("No fire", text_colour=self.cyan)    # Down arrow
        
ch = CO2()
print(2)
print(ch.get_reading())
print(ch.get_reading())
thread = threading.Thread(target=ch.monitor_joystick)
thread.start()
