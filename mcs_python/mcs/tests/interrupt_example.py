#!/usr/bin/python
import RPi.GPIO as GPIO
import time

# Genutzte GPIO Pins
switch = 17  # if GPIO.BCM = 17; if GPIO.BOARD = pin 11
led = 23  # if GPIO.BCM = 23; if GPIO.BOARD = pin 16

# Zaehler-Variable, global
counter = 0
tic = 0

# Pinreferenz waehlen
GPIO.setmode(GPIO.BCM)

# GPIO 17 (Pin 11) als Input definieren und Pullup-Widerstand aktivieren
GPIO.setup(switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# GPIO 23 (Pin 16) als Output definieren als Reaktion auf das Interrupt
GPIO.setup(led, GPIO.OUT)


# Callback-Funktion
def interrupt(channel):
    global counter
    GPIO.output(led, GPIO.HIGH)
    # Counter um eins erhoehen und ausgeben
    counter = counter + 1
    print("Counter " + str(counter))


# Interrupt-Event (switch gedrueckt bzw. aeusserer Einfluss) hinzufuegen, steigende Flanke,
# bouncetime = so lange wird ein erneutes Druecken verhindert
GPIO.add_event_detect(switch, GPIO.FALLING, callback=interrupt, bouncetime=250)

# Default setzen zu Beginn des Programms
GPIO.output(led, GPIO.LOW)

# Endlosschleife, bis Strg-C gedrueckt wird
try:
    while True:
        # nix Sinnvolles tun
        tic = tic + 1
        print("Tic %d" % tic)
        print("input: ", GPIO.input(switch))
        time.sleep(1)
        GPIO.output(led, GPIO.LOW)
except KeyboardInterrupt:
    GPIO.cleanup()
    print("\nBye")