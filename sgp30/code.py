"""
main.py
"""
#print('Blinking LED...')
#import blink
#print('Neopixel pixel demo...')
#import neopixel_pixel
#print('Neopixel rainbow demo...')
#import neopixel_simpletest
#print('Neopixel stream-plasma demo...')
#import stream_plasma
# 2021-0126 PP air quality
#OK: import sgp30_simpletest
#2021-0806 OK: from sgp30_neopixels import run
#from sgp30_neopixels_v2 import run
#print("Air quality measurement... version 2")
#run(baseline=10, verbose=True)

# 2021-0807 add OLED-display
print("Air quality measurement... version 3")
from sgp30_neopixels_v3 import run
run(baseline=10, verbose=True)

# 2021-0808 test OLED using displayio
#print("Test adafruit.displayio... ")
#import displayio_simpletest

# TODO CO2 sensor device using displayio
