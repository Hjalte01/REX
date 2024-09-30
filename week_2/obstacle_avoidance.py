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

left_motor_diff = 0.89

# send a go_diff command to drive forward
leftSpeed = 40*left_motor_diff
rightSpeed = 40


def forward(len):
    distance = 4.5 * len # in meters

    print(arlo.go_diff(leftSpeed, rightSpeed, 1, 1))
    # Wait a bit while robot moves forward
    sleep(distance)

    # send a stop command
    print(arlo.stop_driver())


def turn_left(degree):
    constant_for_turning_90_degree = 1.5
    time_for_turning_one_degree = constant_for_turning_90_degree / 90

    # send a go_diff command to turn left
    print(arlo.go_diff(leftSpeed, rightSpeed, 0, 1))

    # Wait a bit while robot turns left
    sleep(time_for_turning_one_degree*degree)

def turn_right(degree):
    constant_for_turning_90_degree = 1.5
    time_for_turning_one_degree = constant_for_turning_90_degree / 90

    # send a go_diff command to turn right
    print(arlo.go_diff(leftSpeed, rightSpeed, 1, 0))

    # Wait a bit while robot turns right
    sleep(time_for_turning_one_degree*degree)


# Drive forward and turn left if obstacle detected


def drive_around_and_detect_obstacle():
    for i in range(30):
        forward(0.1)
        print("reading front sensor, ", arlo.read_front_ping_sensor())
        if arlo.read_front_ping_sensor() < 200 and arlo.read_right_ping_sensor() < 200 and arlo.read_left_ping_sensor() < 200:
            print("obstacle detected in front, right and left")
            turn_left(180)
            print(arlo.stop_driver())
        elif arlo.read_front_ping_sensor() < 200 and arlo.read_right_ping_sensor() < 200:
            print("obstacle detected in right")
            turn_left(90)
            print(arlo.stop_driver())
        elif arlo.read_front_ping_sensor() < 200 and arlo.read_left_ping_sensor() < 200:
            print("obstacle detected in left")
            turn_right(90)
            print(arlo.stop_driver())
        elif arlo.read_right_ping_sensor() < 200:
            print("obstacle detected in right")
            turn_left(90)
            print(arlo.stop_driver())
        elif arlo.read_left_ping_sensor() < 200:
            print("obstacle detected in left")
            turn_right(90)
            print(arlo.stop_driver())
        elif arlo.read_front_ping_sensor() < 200:
            print("obstacle detected in front")
            turn_right(90)
            print(arlo.stop_driver())



front_sensor = arlo.read_front_ping_sensor()
print("front sensor: ", front_sensor)
