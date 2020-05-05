#! /usr/bin/python2


import time
import sys

EMULATE_HX711=False

referenceUnit = 1

if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711 import HX711
else:
    from emulated_hx711 import HX711

def cleanAndExit():
    print("Cleaning...")

    if not EMULATE_HX711:
        GPIO.cleanup()
        
    print("Bye!")
    sys.exit()
    
def monitor(weight):

    var = 3000     # weight is 3000 > 3kg for food + water,
    # I chose 3kg because I had sensor only up to 3kg,
    # could be more its not an issue, since I only need to
    # monitor when food limit is critically low, not when it is more than upper limit
    if((3000/100*20) > weight):
        print("Low food and water levels")
        print(round(weight, 1))

hx = HX711(11, 12)

hx.set_reading_format("MSB", "MSB")

# HOW TO CALCULATE THE REFFERENCE UNIT
# To set the reference unit to 1. Put 1kg on your sensor or anything you have and know exactly how much it weights.
# In this case, 92 is 1 gram because, with 1 as a reference unit I got numbers near 0 without any weight
# and I got numbers around 184000 when I added 2kg. So,
# If 2000 grams is 184000 then 1000 grams is 184000 / 2000 = 92.
hx.set_reference_unit(referenceUnit)
hx.reset()
hx.tare()

while True:
    try:       
        # Prints the weight.
        val = hx.get_weight(5)
        #val = 10000
        monitor(val)
        #print(val)
        hx.power_down()
        hx.power_up()
        time.sleep(3600) # delay in seconds to keep checking food and water %, chose to monitor every 1 hour

    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
