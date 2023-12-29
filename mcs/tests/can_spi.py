# import spidev
import time
import RPi.GPIO as GPIO

CS_CAN = 8  # GPIO 8 = pin 24
CAN_MSG_INTERRUPT = 25

tic = 0
counter = 0


def read_msg(channel):
    global counter
    print("New CAN message reported by MCP2515")
    # GPIO.output(CS_CAN, GPIO.HIGH)
    # Counter um eins erhoehen und ausgeben
    counter = counter + 1
    print("Counter " + str(counter))

GPIO.setmode(GPIO.BCM)

GPIO.setup(CAN_MSG_INTERRUPT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(CS_CAN, GPIO.OUT)

GPIO.output(CS_CAN, GPIO.LOW)  # SPI on?
GPIO.add_event_detect(CAN_MSG_INTERRUPT, GPIO.FALLING, callback=read_msg, bouncetime=250)

try:
    while True:
        # nix Sinnvolles tun
        tic = tic + 1
        print("Tic %d" % tic)
        time.sleep(1)
        # GPIO.output(CS_CAN, GPIO.LOW)
        # pass

except KeyboardInterrupt:
    # exits when you press CTRL+C or the stop button
    print("Controlled close of the program")

# except:
#     # This catches ALL other exceptions including errors.
#     # You won't get any error messages for debugging
#     # so only use it once your code is working!
#     print("Close with other error or exception occured!")


finally:
    # GPIO.output(CS_CAN, GPIO.LOW)  # SPI off?
    GPIO.cleanup()
    
