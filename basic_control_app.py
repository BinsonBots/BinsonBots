from robot import Robot
from controller import Controller

# Create robot and controller

robot = Robot()
controller = Controller()

while True:

    # Main loop

    left = controller.ly
    right = controller.ry

    robot.set_speeds(left, right)
