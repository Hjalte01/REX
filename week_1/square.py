from time import sleep

import robot

# Create a robot object and initialize
arlo = robot.Robot()

# sleep for 2 seconds
sleep(2)

print("Running ...")

left_motor_diff = 0.9625

# send a go_diff command to drive forward
leftSpeed = 53*left_motor_diff
rightSpeed = 53

for (i) in range(1):
    print(arlo.go_diff(leftSpeed, rightSpeed, 1, 1))

    # Wait a bit while robot moves forward
    sleep(3)

    # send a stop command
    print(arlo.stop())

    # # send a go_diff command to turn left
    # print(arlo.go_diff(leftSpeed, rightSpeed, 0, 1))

    # # Wait a bit while robot turns left
    # sleep(0.94)

# send a stop command
print(arlo.stop())

# # send a go_diff command to turn left
# leftSpeed = 53*left_motor_diff
# rightSpeed = 53
# print(arlo.go_diff(leftSpeed, rightSpeed, 0, 1))

# # Wait a bit while robot moves forward
# sleep(0.94*8)

# # send a stop command
# print(arlo.stop())
