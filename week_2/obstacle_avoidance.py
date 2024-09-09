from time import sleep
import os, sys

# get for the robot module from the parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import robot

# Create a robot object and initialize
arlo = robot.Robot()

# sleep for 2 seconds
sleep(2)

print("Running ...")

left_motor_diff = 0.875

# send a go_diff command to drive forward
leftSpeed = 40*left_motor_diff
rightSpeed = 40


def forward(len):
    distance = 4.5 * len # in meters

    print(arlo.go_diff(leftSpeed, rightSpeed, 1, 1))
    # Wait a bit while robot moves forward
    sleep(distance)

    # send a stop command
    print(arlo.stop())

def turn_left(degree):
    constant_90_degree = 1.5 / 90

    # send a go_diff command to turn left
    print(arlo.go_diff(leftSpeed, rightSpeed, 0, 1))

    # Wait a bit while robot turns left
    sleep(constant_90_degree*degree)


# Get sensor data


for i in range(30):
    forward(0.1)
    print("reading front sensor, ", arlo.read_front_ping_sensor())
    if arlo.read_front_ping_sensor() < 200:
        print("obstacle detected in front")
        print(arlo.stop())
        break
    if arlo.read_right_ping_sensor() < 200:
        print("obstacle detected in right")
        print(arlo.stop())
        break
    if arlo.read_left_ping_sensor() < 200:
        print("obstacle detected in left")
        print(arlo.stop())
        break

