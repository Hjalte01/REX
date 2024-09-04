from time import sleep

import robot

# Create a robot object and initialize
arlo = robot.Robot()

print("Running ...")

left_motor_diff = 0.98

# send a go_diff command to drive forward
leftSpeed = 53*left_motor_diff
rightSpeed = 53
print(arlo.go_diff(leftSpeed, rightSpeed, 1, 1))

# Wait a bit while robot moves forward
sleep(3)

# send a stop command
print(arlo.stop())

# # Wait a bit before next command
# sleep(0.041)

# # send a go_diff command to turn 90 degrees to the left
# leftSpeed = 64
# rightSpeed = 32
# print(arlo.go_diff(leftSpeed, rightSpeed, 1, 0))

# # Wait a bit while robot turns
# sleep(3)

# send a stop command
print(arlo.stop())
