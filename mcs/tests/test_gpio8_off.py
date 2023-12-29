import RPi.GPIO as GPIO

CS_CAN = 12  # GPIO 8 = pin 24

GPIO.setmode(GPIO.BCM)


GPIO.setup(CS_CAN, GPIO.OUT)
try:
    GPIO.output(CS_CAN, GPIO.LOW)

finally:
    GPIO.cleanup()
