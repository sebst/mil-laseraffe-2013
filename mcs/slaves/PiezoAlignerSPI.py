import spidev
import time
import RPi.GPIO as GPIO

# NOTE: All channel numbers are GPIO-numbers not Pin-numbers!
#       Example: 21 = GPIO21 ans NOT pin nr = 21 on the pcb !!!

# # Chip Select (CS or SS) for voltage setting with SPI
# CS_DAC_DRV1 = 21
# CS_DAC_DRV2 = 16
# CS_DAC_DRV3 = 23

# # Default Chip Select (CS or SS) for CAN communication of SPI
# CS_CAN = 8

# Piezo Driver Channel
EN_DRV1 = 19
EN_DRV2 = 24
EN_DRV3 = 14

# Gain setter channels for the appropriate 3 driver channel
# --> 4 possible combinations for each driver
#       --> 0 + 0; 1 + 0; 0 + 1 and 1 + 1
GAIN0_DRV1 = 20  # Gain setter channel A for piezo driver 0 (drv_gain = 0-3)
GAIN1_DRV1 = 26  # Gain setter channel B for piezo driver 0 (drv_gain = 0-3)
GAIN0_DRV2 = 7   # Gain setter channel A for piezo driver 1 (drv_gain = 0-3)
GAIN1_DRV2 = 12  # Gain setter channel B for piezo driver 1 (drv_gain = 0-3)
GAIN0_DRV3 = 15  # Gain setter channel A for piezo driver 2 (drv_gain = 0-3)
GAIN1_DRV3 = 18  # Gain setter channel B for piezo driver 2 (drv_gain = 0-3)

# LED at GPIO13
LED = 13

# Piezo select setter for 4 different piezo types of the 3 piezo channels
# --> 4 possible combinations for each driver
#       --> 0 + 0; 1 + 0; 0 + 1 and 1 + 1

# A + B
# 0 + 0 = -20V until 100V
# 1 + 0 = -20V until  75V
# 0 + 1 =   0V until 100V
# 1 + 1 =   0V until  75V
PI_SEL10 = 5   # Piezoconfig setter channel A for piezo channel 1
PI_SEL11 = 6   # Piezoconfig setter channel B for piezo channel 1
PI_SEL20 = 27  # Piezoconfig setter channel A for piezo channel 2
PI_SEL21 = 22  # Piezoconfig setter channel B for piezo channel 2
PI_SEL30 = 4   # Piezoconfig setter channel A for piezo channel 3
PI_SEL31 = 17  # Piezoconfig setter channel B for piezo channel 3


# Set pin number mode to GPIO-numbers
GPIO.setmode(GPIO.BCM)

# Define/setup the used channels

# GPIO.setup(CS_CAN, GPIO.OUT)
# GPIO.setup(CS_DAC_DRV1, GPIO.OUT)
# GPIO.setup(CS_DAC_DRV2, GPIO.OUT)
# GPIO.setup(CS_DAC_DRV3, GPIO.OUT)
GPIO.setup(EN_DRV1, GPIO.OUT)
GPIO.setup(EN_DRV2, GPIO.OUT)
GPIO.setup(EN_DRV3, GPIO.OUT)
GPIO.setup(GAIN0_DRV1, GPIO.OUT)
GPIO.setup(GAIN1_DRV1, GPIO.OUT)
GPIO.setup(GAIN0_DRV2, GPIO.OUT)
GPIO.setup(GAIN1_DRV2, GPIO.OUT)
GPIO.setup(GAIN0_DRV3, GPIO.OUT)
GPIO.setup(GAIN1_DRV3, GPIO.OUT)
GPIO.setup(LED, GPIO.OUT)
GPIO.setup(PI_SEL10, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PI_SEL11, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PI_SEL20, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PI_SEL21, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PI_SEL30, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PI_SEL31, GPIO.IN, pull_up_down=GPIO.PUD_UP)

counter = 0
channel = 1
driver_gain1 = 3
driver_gain2 = 3
driver_gain3 = 3
driver_en1 = 0
driver_en2 = 0
driver_en3 = 0
dac_gain1 = 1
dac_gain2 = 1
dac_gain3 = 1
value1 = 0
value2 = 0
value3 = 0
dir1 = 0
dir2 = 0
dir3 = 0
piezoconfig1 = 0
piezoconfig2 = 0
piezoconfig3 = 0
wr_dac = 0

class bcolors:
    INPUT = '\033[32m' #GREEN
    FAIL = '\033[91m' #RED
    RESET = '\033[0m' #RESET COLOR
    
spi_1 = spidev.SpiDev()
spi_2 = spidev.SpiDev()
spi_3 = spidev.SpiDev()

# spi.open(0, 0)  # GPIO 8: CAN-controller
# spi.open(0, 1)  # GPIO 7: not used
spi_1.open(0, 2)  # GPIO 21: Piezzo 1
spi_2.open(0, 3)  # GPIO 16: Piezzo 2
spi_3.open(0, 4)  # GPIO 23: Piezzo 3

# spi.no_cs = True # no shipselect
spi_1.max_speed_hz = 122000
spi_2.max_speed_hz = 122000
spi_3.max_speed_hz = 122000


def enable_piezodriver(channel, drv_en): #channel[1-3], drv_en[0,1]
    if channel == 1:
        if drv_en == 1:
            driver_en1 = 1
            GPIO.output(EN_DRV1, GPIO.HIGH)
        else:
            driver_en1 = 0
            GPIO.output(EN_DRV1, GPIO.LOW)
              
    if channel == 2:
        if drv_en == 1:
            driver_en2 = 1
            GPIO.output(EN_DRV2, GPIO.HIGH)
        else:
            driver_en2 = 0
            GPIO.output(EN_DRV2, GPIO.LOW)      
            
    if channel == 3:
        if drv_en == 1:
            driver_en3 = 1
            GPIO.output(EN_DRV3, GPIO.HIGH)
        else:
            driver_en3 = 0
            GPIO.output(EN_DRV3, GPIO.LOW)


def set_driver_gain(channel, drv_gain): #channel[1-3], drv_gain[0-3]
    if channel == 1:
        if drv_gain == 0:
            GPIO.output(GAIN0_DRV1, GPIO.LOW)
            GPIO.output(GAIN1_DRV1, GPIO.LOW)
        if drv_gain == 1:
            GPIO.output(GAIN0_DRV1, GPIO.HIGH)
            GPIO.output(GAIN1_DRV1, GPIO.LOW)        
        if drv_gain == 2:
            GPIO.output(GAIN0_DRV1, GPIO.LOW)
            GPIO.output(GAIN1_DRV1, GPIO.HIGH)
        if drv_gain == 3:
            GPIO.output(GAIN0_DRV1, GPIO.HIGH)
            GPIO.output(GAIN1_DRV1, GPIO.HIGH)
        
    if channel == 2:
        if drv_gain == 0:
            GPIO.output(GAIN0_DRV2, GPIO.LOW)
            GPIO.output(GAIN1_DRV2, GPIO.LOW)
        if drv_gain == 1:
            GPIO.output(GAIN0_DRV2, GPIO.HIGH)
            GPIO.output(GAIN1_DRV2, GPIO.LOW)        
        if drv_gain == 2:
            GPIO.output(GAIN0_DRV2, GPIO.LOW)
            GPIO.output(GAIN1_DRV2, GPIO.HIGH)
        if drv_gain == 3:
            GPIO.output(GAIN0_DRV2, GPIO.HIGH)
            GPIO.output(GAIN1_DRV2, GPIO.HIGH)
            
    if channel == 3:
        if drv_gain == 0:
            GPIO.output(GAIN0_DRV3, GPIO.LOW)
            GPIO.output(GAIN1_DRV3, GPIO.LOW)
        if drv_gain == 1:
            GPIO.output(GAIN0_DRV3, GPIO.HIGH)
            GPIO.output(GAIN1_DRV3, GPIO.LOW)        
        if drv_gain == 2:
            GPIO.output(GAIN0_DRV3, GPIO.LOW)
            GPIO.output(GAIN1_DRV3, GPIO.HIGH)
        if drv_gain == 3:
            GPIO.output(GAIN0_DRV3, GPIO.HIGH)
            GPIO.output(GAIN1_DRV3, GPIO.HIGH)


def write_dac(channel, value, direction, dac_gain): #channel[1-3], value[0-4095], direction[0,1], dac_gain[1,2]
    msb = (((value >> 8) &0xFF) | (direction << 7) | ((2-dac_gain) << 5) | (1 << 4))    
    lsb = (value & 0xFF)

    if channel == 1:
        # GPIO.output(CS_DAC_DRV1, GPIO.LOW)
        spi_1.xfer2([msb, lsb])
                
    if channel == 2:
        # GPIO.output(CS_DAC_DRV2, GPIO.LOW)
        spi_2.xfer2([msb, lsb])
                  
    if channel == 3:
        # GPIO.output(CS_DAC_DRV3, GPIO.LOW)
        spi_3.xfer2([msb, lsb])

    # GPIO.output(CS_DAC_DRV1, GPIO.HIGH)
    # GPIO.output(CS_DAC_DRV2, GPIO.HIGH)
    # GPIO.output(CS_DAC_DRV3, GPIO.HIGH)


print("--------------- Program started ----------------------")

# Set default values at the beginning

# GPIO.output(CS_DAC_DRV1, GPIO.HIGH)
# GPIO.output(CS_DAC_DRV2, GPIO.HIGH)
# GPIO.output(CS_DAC_DRV3, GPIO.HIGH)
# GPIO.output(CS_CAN, GPIO.HIGH)

GPIO.output(EN_DRV1, GPIO.LOW)
GPIO.output(EN_DRV2, GPIO.LOW)
GPIO.output(EN_DRV3, GPIO.LOW)
GPIO.output(GAIN0_DRV1, GPIO.LOW)
GPIO.output(GAIN1_DRV1, GPIO.LOW)
GPIO.output(GAIN0_DRV2, GPIO.LOW)
GPIO.output(GAIN1_DRV2, GPIO.LOW)
GPIO.output(GAIN0_DRV3, GPIO.LOW)
GPIO.output(GAIN1_DRV3, GPIO.LOW)
GPIO.output(LED, GPIO.HIGH)


write_dac(1, 0, 0, 1)  # channel[1-3], value[0-4095], direction[0,1], dac_gain[1,2]
write_dac(1, 0, 1, 1)
write_dac(2, 0, 0, 1)  # channel[1-3], value[0-4095], direction[0,1], dac_gain[1,2]
write_dac(2, 0, 1, 1)
write_dac(3, 0, 0, 1)  # channel[1-3], value[0-4095], direction[0,1], dac_gain[1,2]
write_dac(3, 0, 1, 1)
set_driver_gain(1, 3)  # channel[1-3], drv_gain[0-3]
set_driver_gain(2, 3)  # channel[1-3], drv_gain[0-3]
set_driver_gain(3, 3)  # channel[1-3], drv_gain[0-3]
enable_piezodriver(1, 0)  # channel[1-3], drv_en[0,1]
enable_piezodriver(2, 0)  # channel[1-3], drv_en[0,1]
enable_piezodriver(3, 0)  # channel[1-3], drv_en[0,1]

try:
    while True:
        piezoconfig1 = 3-((GPIO.input(PI_SEL10)) | ((GPIO.input(PI_SEL11)) << 1))
        piezoconfig2 = 3-((GPIO.input(PI_SEL20)) | ((GPIO.input(PI_SEL21)) << 1))
        piezoconfig3 = 3-((GPIO.input(PI_SEL30)) | ((GPIO.input(PI_SEL31)) << 1))
        print("")
        print("Welcher Parameter soll geändert werden?")
        print("<c> Aktueller Kanal [1-3]   ", channel)

        if channel == 1:
            driver_en = driver_en1
            driver_gain = driver_gain1
            dac_gain = dac_gain1
            value = value1
            dir0 = dir1
            piezoconfig = piezoconfig1

        if channel == 2:
            driver_en = driver_en2
            driver_gain = driver_gain2
            dac_gain = dac_gain2
            value = value2
            dir0 = dir2
            piezoconfig = piezoconfig2

        if channel == 3:
            driver_en = driver_en3
            driver_gain = driver_gain3
            dac_gain = dac_gain3
            value = value3
            dir0 = dir3
            piezoconfig = piezoconfig3

        print("<e> Treiber ein/aus [0,1]   ", driver_en)
        print("<g> Gain des Treibers [0-3] ", driver_gain)
        print("<h> Gain des DACs [1,2]     ", dac_gain)
        print("<v> DAC-Wert [0-4095]       ", value)
        print("<d> Richtung [0,1]          ", dir0)
        print("    Piezotyp (read only)    ", piezoconfig)
        print("<r> Redraw                  ")
        eingabe = input(bcolors.INPUT + "Eingabe: " + bcolors.RESET)

        if eingabe == "c":
            eingabe = int(input(bcolors.INPUT + "Wähle Kanal 1-3 " + bcolors.RESET))
            if (eingabe >= 1) and (eingabe <= 3):
                channel = eingabe
            else:
                print(bcolors.FAIL + "Falsche Eingabe!" + bcolors.RESET)

        elif eingabe == "e":
            eingabe = int(input(bcolors.INPUT + "Treiber ein = 1, Treiber aus = 0: " + bcolors.RESET))
            if (eingabe == 0) or (eingabe == 1):
                if channel == 1:
                    driver_en1 = eingabe
                if channel == 2:
                    driver_en2 = eingabe
                if channel == 3:
                    driver_en3 = eingabe
                enable_piezodriver(channel, eingabe) #channel[1-3], drv_en[0,1]

        elif eingabe == "g":
            eingabe = int(input(bcolors.INPUT + "Treiber-Gain 0-3: " + bcolors.RESET))
            if (eingabe >= 0) and (eingabe <= 3):
                if channel == 1:
                    driver_gain1 = eingabe
                if channel == 2:
                    driver_gain2 = eingabe
                if channel == 3:
                    driver_gain3 = eingabe
                set_driver_gain(channel, eingabe) #channel[1-3], drv_gain[0-3]
            else:
                print(bcolors.FAIL + "Falsche Eingabe!" + bcolors.RESET)

        elif eingabe == "h":
            eingabe = int(input(bcolors.INPUT + "DAC-Gain 1,2: " + bcolors.RESET))
            if (eingabe == 1) or (eingabe == 2):
                wr_dac = 1
                if channel == 1:
                    dac_gain1 = eingabe
                if channel == 2:
                    dac_gain2 = eingabe
                if channel == 3:
                    dac_gain3 = eingabe
            else:
                print(bcolors.FAIL + "Falsche Eingabe!" + bcolors.RESET)

        elif eingabe == "v":
            eingabe = int(input(bcolors.INPUT + "Value 0-4095: " + bcolors.RESET))
            if (eingabe >= 0) and (eingabe <= 4095):
                wr_dac = 1
                if channel == 1:
                    value1 = eingabe
                if channel == 2:
                    value2 = eingabe
                if channel == 3:
                    value3 = eingabe
            else:
                print(bcolors.FAIL + "Falsche Eingabe!" + bcolors.RESET)

        elif eingabe == "d":
            eingabe = int(input(bcolors.INPUT + "Richtung Horizontal = 0, Vertikal = 1: " + bcolors.RESET))
            if (eingabe == 0) or (eingabe == 1):
                wr_dac = 1
                if channel == 1:
                    dir1 = eingabe
                if channel == 2:
                    dir2 = eingabe
                if channel == 3:
                    dir3 = eingabe
            else:
                print(bcolors.FAIL + "Falsche Eingabe!" + bcolors.RESET)

        elif eingabe == "r":
                wr_dac = 0 # irgendein Blödsinn machen

        else:
            print(bcolors.FAIL + "Falsche Eingabe!" + bcolors.RESET)

        if wr_dac == 1:
            wr_dac = 0
            if channel == 1:
                write_dac(1, value1, dir1, dac_gain1) #channel[1-3], value[0-4095], direction[0,1], dac_gain[1,2]
            if channel == 2:
                write_dac(2, value2, dir2, dac_gain2)
            if channel == 3:
                write_dac(3, value3, dir3, dac_gain3)

except KeyboardInterrupt:
    # exits when you press CTRL+C or the stop button
    print("--------------- Program stopped ----------------------")
    print("Controlled close of the program")

except:
    # This catches ALL other exceptions including errors.
    # You won't get any error messages for debugging
    # so only use it once your code is working!
    print("Close with other error or exception occured!")

finally:
    GPIO.cleanup()
