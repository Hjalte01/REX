from time import sleep

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
    

def square():
    for i in range(4):
        forward(1)
        print(arlo.stop())
        sleep(1)
        turn_left(90)
        print(arlo.stop())
        sleep(1)


# The number 8
def left_forward_turn(time):

    # send a go_diff command to turn left
    print(arlo.go_diff(leftSpeed, rightSpeed*1.8, 1, 1))

    # Wait a bit while robot turns left
    sleep(time)

def right_forward_turn(time):

    # send a go_diff command to turn left
    print(arlo.go_diff(leftSpeed*1.87, rightSpeed, 1, 1))

    # Wait a bit while robot turns left
    sleep(time)

# Left circle of the number 8
# left_forward_turn(10)

# Right circle of the number 8
right_forward_turn(10)

# send a stop command
print(arlo.stop())
