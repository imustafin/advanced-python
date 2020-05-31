import os


def myshell_exit():
    print("Goodbye!")


def myshell_run():
    while True:
        try:
            command = input("myshell: ")
            if command == "exit":
                break
            os.system(command)
        except EOFError:
            break
    myshell_exit()


if __name__ == '__main__':
    myshell_run()