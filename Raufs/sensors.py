from sense_hat import SenseHat
from time import sleep
sense = SenseHat()

class CO2:

        orange = (254, 110, 0)
        cyan = (0, 255, 255)
        co2_ppm = 500   # Good CO2 ppm

        def _init_(self):
                while True:
                        for event in sense.stick.get_events():
                                # Check if the joystick was pressed
                                if event.action == "pressed":
                
                                        # Check which direction
                                        if event.direction == "up":
                                                sense.show_message("Fire", orange)      # Up arrow
                                                co2_ppm = 8000         # High CO2 ppm - fire present 
                                        elif event.direction == "down":
                                                sense.show_letter("No fire", cyan)      # Down arrow
                                                co2_ppm = 500

        def get_reading(self):
                return co2_ppm


        