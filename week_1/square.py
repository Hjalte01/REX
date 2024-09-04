from time import sleep

import robot

# Create a robot object and initialize
arlo = robot.Robot()

# sleep for 2 seconds
sleep(2)

print("Running ...")

left_motor_diff = 0.94

# send a go_diff command to drive forward
leftSpeed = 53*left_motor_diff
rightSpeed = 53


def forward(len):
    distance = 3 * len # in meters

    print(arlo.go_diff(leftSpeed, rightSpeed, 1, 1))
    # Wait a bit while robot moves forward
    sleep(distance)

    # send a stop command
    print(arlo.stop())

def turn_left(degree):
    constant_90_degree = 0.911 / 90

    # send a go_diff command to turn left
    print(arlo.go_diff(leftSpeed, rightSpeed, 0, 1))

    # Wait a bit while robot turns left
    sleep(constant_90_degree*degree)
    

def square():
    for i in range(4):
        forward(1)
        turn_left(90)


# call the square function
square()

# send a stop command
print(arlo.stop())
