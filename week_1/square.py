from time import sleep

import robot

# Create a robot object and initialize
arlo = robot.Robot()

print("Running ...")

left_motor_diff = 0.96

# send a go_diff command to drive forward
leftSpeed = 53*left_motor_diff
rightSpeed = 53
print(arlo.go_diff(leftSpeed, rightSpeed, 1, 1))

# Wait a bit while robot moves forward
sleep(3)

# send a stop command
print(arlo.stop())

# send a go_diff command to turn left
leftSpeed = 53*left_motor_diff
rightSpeed = 53
print(arlo.go_diff(leftSpeed, rightSpeed, 0, 1))

# Wait a bit while robot moves forward
sleep(0.8)

# send a stop command
print(arlo.stop())
