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

def get_sensor_data():
    read_front_ping_sensor = arlo.read_front_ping_sensor()
    read_left_ping_sensor = arlo.read_left_ping_sensor()
    read_right_ping_sensor = arlo.read_right_ping_sensor()

    print("Front sensor: ", read_front_ping_sensor)
    print("Left sensor: ", read_left_ping_sensor)
    print("Right sensor: ", read_right_ping_sensor)


for i in range(4):
    forward(0.2)
    if arlo.read_front_ping_sensor() < 40:
        print(arlo.stop())
        break

