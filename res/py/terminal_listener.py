class Terminal_listener():
    def __init__(self, device_commands):
        self.device_commands = device_commands

    def commandListener(self):

        commands = self.device_commands.commands

        print("commands added")

        while True:

            i = 0

            command_str = "Commands: \n"

            for command in commands:
                command_str += f"{i}: {command['desc']} \n"
                i += 1

            # print(command_str)
            # print_handler.add_str(command_str, "commands", 0, True)

            action = input("enter option: ")

            option = int(action)

            commands[option]["func"]()