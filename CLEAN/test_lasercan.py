from lib_laser import LaserBoard
import time


lb = LaserBoard()

lb = LaserBoard(turn_on=True)
for i in range(4):
    lb.set_target_temperature(25)
    print(lb.get_red_blue_temperature())

    print(lb.blue_laser.get_temperature_laser_1())
    time.sleep(1)
