import os


def myshell_exit():
    print("Goodbye!")


def get_short_path():
    path = os.getcwd().split("/")
    parts = [x[:2] if x.startswith(".") else x[:1] for x in path]
    return "/".join(parts)


def cd(command):
    params = command.split()[1:]
    path = params[0] if params else os.environ['HOME']
    try:
        os.chdir(path)
    except OSError as e:
        print(e)


def myshell_run():
    while True:
        try:
            command = input(f"myshell [{get_short_path()}]: ")
            if command.startswith("cd ") or command == "cd":
                cd(command)
                continue
            if command == "exit":
                break
            os.system(command)
        except EOFError:
            break
    myshell_exit()


if __name__ == '__main__':
    myshell_run()