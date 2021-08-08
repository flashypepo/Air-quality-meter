"""
sgp30_neopixels.py - measure air quality and convert to color on neopixel

The neostick indicates the CO2 concentration based on the following table

400 - 1000 ppm: green   (neopixel 1-3)
1000 - 1600 ppm: yellow (neopixel 4-6)
>1600 ppm: red LEDs (neopixel 7+8)

neopixel  eCO2 range   led-color
 1        400 - 600     green  ok
 2        600 - 800     green  ok
 3        800 - 1000    green  ok
 4        1000 - 1300   yellow Complaints of drowsiness and poor air.
 5        1300 - 1600   yellow 
 6        1600 - 2000   orange
 7+8      >2000         red - Headaches, sleepiness and stagnant, stale, stuffy air

Source:
https://www.kane.co.uk/knowledge-centre/what-are-safe-levels-of-co-and-co2-in-rooms

TODO: OO-versies with classes DisplayOLED, DisplayNeoPixels, SGP30Sensor

2021-0808 PP version 3 - add SSD1306 OLED-display, rotation = 3 (180 degrees)
2021-0806 PP version 2 - Neopixel stick, neopixels accordng to CO2 table
2021-0126 PP new
"""
import time
import board
import busio
import neopixel

# 2021-0807 TODO lateron - too complicated at the moment
"""
import displayio
import terminalio
from adafruit_display_text import label
import adafruit_displayio_ssd1306
"""
import adafruit_sgp30
import adafruit_ssd1306
from colors import RED, GREEN, BLACK, YELLOW, ORANGE

#displayio.release_displays()

# ==================
# Neopixel functions
# ==================
def leds_to_lit(eco2=400):
    """
    leds_to_lit(eco2) - maps eCO2-value to number of neopixels to lit,
    according to table in header
    params: eco2, eCO2-value, defautl=400 ppm
    returns: N, number of neopixels
    TODO: there must be a clever way to map eCO2 to N
    """
    N = 0
    if eco2 < 600:
        N = 1
    elif eco2 < 800:
        N = 2
    elif eco2 < 1000:
        N = 3
    elif eco2 < 1300:
        N = 4
    elif eco2 < 1600:
        N = 5
    elif eco2 < 2000:
        N = 6
    else:  # eCO2 > 2000
        N = 8
    return N

def lightBarGraph(N):
    """
    lightBarGraph(N) - lit N neopixels, color according to table in header
    params: N, number of neopixels to lit
    
    TODO: there must be  clever way to lit the varous neopixels
    """
    # start with all pixels off
    pixels_off()
    # lit neopixels with specifc color according to N and table in header
    if N == 1:
        pixels[0] = GREEN
    elif N == 2:
        pixels[0] = GREEN
        pixels[1] = GREEN
    elif N == 3:
        pixels[0] = GREEN
        pixels[1] = GREEN
        pixels[2] = GREEN
    elif N == 4:
        pixels[0] = GREEN
        pixels[1] = GREEN
        pixels[2] = GREEN
        pixels[3] = YELLOW
    elif N == 5:
        pixels[0] = GREEN
        pixels[1] = GREEN
        pixels[2] = GREEN
        pixels[3] = YELLOW        
        pixels[4] = YELLOW
    elif N == 6:
        pixels[0] = GREEN
        pixels[1] = GREEN
        pixels[2] = GREEN
        pixels[3] = YELLOW        
        pixels[4] = YELLOW
        pixels[5] = ORANGE
    elif N == 8:
        pixels[0] = GREEN
        pixels[1] = GREEN
        pixels[2] = GREEN
        pixels[3] = YELLOW        
        pixels[4] = YELLOW
        pixels[5] = ORANGE
        pixels[6] = ORANGE
        pixels[7] = RED
    # show the pixels
    pixels.show()

def pixels_off(color=BLACK):
    """
    pixelsOff(color) - set color of neopixels.
    params: color, color of the neopixels, BLACK is neopixels off
    """
    pixels.fill(color)
    pixels.show()


# ==================
# sensor: SGP30
# ==================

# SGP30 sensor via I2C
# 2021-0126 PP: SGP30 Lolin-shield - SDA or SCL needs a pull up
#           SGP30 connected via STEMMA-Grove adaptor board.
#i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
i2c = busio.I2C(board.SCL, board.SDA)

# SGP30 sensor
sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)
sgp30.iaq_init()
sgp30.set_iaq_baseline(0x8973, 0x8AAE)
print("SGP30 serial #", [hex(i) for i in sgp30.serial])

# ==================
# Neopixel device
# DIN neopixels connected to GPIO D8
# Neopixel stick: 8 neopixels
# ==================
pixel_pin = board.D0
num_pixels = 8 # neostick
ORDER = neopixel.GRB
pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=0.2,
    auto_write=False, pixel_order=ORDER
)
#pixels.auto_write = False
#pixels.byte_order = ORDER
pixels_off()

# ==================
# OLED SSD1306 display
# Bus: i2c, default i2c-address = 03xC
# ==================
displayWidth = 128
displayHeight = 32
display = adafruit_ssd1306.SSD1306_I2C(displayWidth, displayHeight, i2c)
# Alternatief:
# display = adafruit_ssd1306.SSD1306_I2C(displayWidth, displayHeight, i2c, addr=0x3C)
# 2021-0808 TEST: display.rotation = 2  # 2021-0808 rotate display180 degree (my PIOLED display)
display.fill(0)
display.show()

# OLED display: draw border
def border():
    display.rect(0, 0, displayWidth, displayHeight, True)

# Main application
def run(baseline=10, verbose=False):
    """
    run() - reads every 1 second:
                * values from sensor,
                * display them on OLED-display,
                * display eCO2-level on neopixel stick.

    params:
        baseline, number of seconds before SGP30 baseline values are read, default:10 sec
        verbose, details of process are printed on console, default: no details
    """
    try:
        elapsed_sec = 0
        # initial baseline values
        baseline_eCO2 = sgp30.baseline_eCO2
        baseline_TVOC = sgp30.baseline_TVOC
        while True:
            # get airquality values from sensor
            #eco2 = sgp30.eCO2
            #tvoc = sgp30.TVOC
            eco2, tvoc = sgp30.iaq_measure()
            if verbose is True:
                print("eCO2 = %d ppm \t TVOC = %d ppb" % (eco2, tvoc))
            
            # show values on OLED-display
            display.fill(0)
            border()
            display.text("eCO2:{:} ppm".format(eco2), 5, 5, 1, size=1)
            display.text("TVOC:{:} ppb".format(tvoc), 5, 20, 1, size=1)
            display.show()

            # display eCO2-level on nepixel stick
            leds = leds_to_lit(eco2)
            lightBarGraph(leds)
            
            time.sleep(1)
            
            # console: baseline values every 'baseline' seconds
            elapsed_sec += 1
            if (elapsed_sec > baseline) & (verbose is True):
                elapsed_sec = 0
                baseline_eCO2 = sgp30.baseline_eCO2
                baseline_TVOC = sgp30.baseline_TVOC
                print(
                    "**** Baseline values: eCO2 = 0x%x, TVOC = 0x%x"
                    % (baseline_eCO2, baseline_TVOC)
                    #ORG: % (sgp30.baseline_eCO2, sgp30.baseline_TVOC)
                )

    except KeyboardInterrupt:
        pixels_off()
        print("Store baseline values eCO2:{0:0x} and TVOC: {1:0x}...".format(baseline_eCO2,
                                                                       baseline_TVOC))
        sgp30.set_iaq_baseline(baseline_eCO2, baseline_TVOC)
        print("User interrrupt: done!")
