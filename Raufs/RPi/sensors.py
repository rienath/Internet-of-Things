from sense_hat import SenseHat
from time import sleep
from threading import Thread
import smbus
import math


sense = SenseHat()

# CO2 air sensor model.
# start() to simulate CO2 sensor with joystick in a background thread
class CO2(Thread):
        
        # RGB colours
        orange = [254, 110, 0]
        cyan = [0, 255, 255]
        co2_ppm = 500   # Good CO2 ppm

        # Starts joystick_as_sensor() in a background thread when CO2().start() is ran
        def run(self):
                self.joystick_as_sensor()

        # Gets current CO2 ppm reading
        def get_reading(self):
                return self.co2_ppm

        # Since I do not have CO2 sensor, joystick controlls the ppm measure.
        # If up is pressed, ppm becomes 8000, if down - 500.
        def joystick_as_sensor(self):
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

class Magnetometers():
        
        bus = smbus.SMBus(1)
        
        # MPU6050 Registers, Values and Addresses
        Register_A     = 0              # Address of Configuration register A
        Register_B     = 0x01           # Address of configuration register B
        Register_mode  = 0x02           # Address of mode register

        Device_Address = 0x1e           # HMC5883L magnetometer device address
        Value_A = 0x70                  # Register A value to write
        Value_B = 0xa0                  # Register B value to write

        X_axis_H    = 0x03              # Address of X-axis MSB data register
        Z_axis_H    = 0x05              # Address of Z-axis MSB data register
        Y_axis_H    = 0x07              # Address of Y-axis MSB data register


        def __init__(self):
                # Write to Configuration Register A
                self.bus.write_byte_data(self.Device_Address, self.Register_A, self.Value_A)
                # Write to Configuration Register B for gain
                self.bus.write_byte_data(self.Device_Address, self.Register_B, self.Value_B)
                # Write to mode Register for selecting mode
                self.bus.write_byte_data(self.Device_Address, self.Register_mode, 0)

        # Get raw reading from the sensor
        def __read_raw_data(self, addr):
                # Read raw 16-bit value
                high = self.bus.read_byte_data(self.Device_Address, addr)
                low = self.bus.read_byte_data(self.Device_Address, addr+1)
                # Concatenate higher and lower value
                value = ((high << 8) | low)
                # Get signed value from module
                if(value > 32768):
                    value = value - 65536
                return value

        # Returns force field from HMC5883L magnetometer
        def __get_external_magnetometer(self):
                # So all the differently calibrated magnetometers give roughly same values
                conversion_factor = 2/13
                # Read magnetometer raw value
                x = self.__read_raw_data(self.X_axis_H)
                z = self.__read_raw_data(self.Z_axis_H)
                y = self.__read_raw_data(self.Y_axis_H)
                # Calculate force
                force = math.sqrt(x**2 + y**2 + z**2) * conversion_factor
                return force

        # Returns force field from SenseHat magnetometer
        def __get_internal_magnetometer(self):
                conversion_factor = 1
                compass = sense.get_compass_raw()
                force = math.sqrt(compass['x']**2 + compass['y']**2 + compass['z']**2) * conversion_factor
                return force

        # Returns a list of force fields from all magnetometers
        def get_magnetometers(self):
                # Make a list with all (2) magnetometer readings 
                data = [self.__get_internal_magnetometer(), self.__get_external_magnetometer()]
                return data
        
# Sensors class
class Sensors():
        
        air = CO2()
        magnets = Magnetometers()

        def __init__(self):
                # Start the air sensor emulator controlled by joystick in another thread
                self.air.start()
        
        # Air sensor readings
        def get_air_reading(self):
                return self.air.get_reading()

        # List with magnetometer readings
        def get_magnetometer_reading(self):
                return self.magnets.get_magnetometers()

        
# Test
def main():
        test = Sensors()
        print(test.get_air_reading())
        print(test.get_magnetometer_reading())

#main()
