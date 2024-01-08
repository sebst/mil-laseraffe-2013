import RPi.GPIO as GPIO
import time

switch = 17  # if GPIO.BCM = 17; if GPIO.BOARD = pin 11
led = 23  # if GPIO.BCM = 23; if GPIO.BOARD = pin 16

GPIO.setmode(GPIO.BCM)
GPIO.setup(switch, GPIO.IN)
GPIO.setup(led, GPIO.OUT)

# Answers codes:
# 0 = GPIO.OUT
# 1 = GPIO.IN
# 40 = GPIO.SERIAL
# 41 = GPIO.SPI
# 42 = GPIO.I2C
# 43 = GPIO.HARD_PWM
# -1 = GPIO.UNKNOWN
func = GPIO.gpio_function(led)
print(func)

try:
    while True:
        GPIO.wait_for_edge(switch, GPIO.RISING, timeout=500)
        # print("Something happend or time is up")
        print("switch state", GPIO.input(switch))
        if GPIO.input(switch) == 1:
            GPIO.output(led, GPIO.HIGH)
        else:
            GPIO.output(led, GPIO.LOW)
        time.sleep(0.5)


except KeyboardInterrupt:
    # exits when you press CTRL+C or the stop button
    print("Controlled close of the program")

except:
    # This catches ALL other exceptions including errors.
    # You won't get any error messages for debugging
    # so only use it once your code is working!
    print("Close with other error or exception occured!")


finally:
    GPIO.cleanup()
