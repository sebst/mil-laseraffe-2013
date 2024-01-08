import RPi.GPIO as GPIO

CS_CAN = 8  # GPIO 8 = pin 24

GPIO.setmode(GPIO.BCM)


GPIO.setup(CS_CAN, GPIO.OUT)
try:
    GPIO.output(CS_CAN, GPIO.HIGH)

finally:
    #GPIO.cleanup()
    pass