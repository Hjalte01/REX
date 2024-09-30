from extended_robot import ExtendedRobot

if __name__ == "__main__":
    robot = ExtendedRobot()

    print("Usage:\n\t\033[01m\033[34mg\033[00mo x y\n\t\033[01m\033[34ms\033[00mtop\n\t\033[01m\033[31mq\033[00muit")

    while True:
        user_input = input().strip().lower()
        if user_input[0] == 'g':
            arr = [int(x) for x in user_input.split(" ")[1:] + [40, 40]]
            robot.go(arr[0], arr[1])
        elif user_input[0] == 's':
            robot.stop_driver()
        elif user_input[0] == 'q':
            robot.stop_driver()
            break
