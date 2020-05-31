import subprocess
import os
from time import localtime, strftime
import sys


def myshell_exit():
    print("Goodbye!")


def get_short_path():
    path = os.getcwd().split("/")
    parts = [x[:2] if x.startswith(".") else x[:1] for x in path]
    return "/".join(parts)


def run_log(f, log_file):
    time = strftime("[%Y-%m-%d %H:%M:%S]", localtime())
    cmd, args, lines, pid, returncode = f()
    log_file.write(f"{time} cmd: {cmd}, args: {' '.join(args)}, stdout: {lines}, pid: {pid}, exit: {returncode} \n")
    log_file.flush()


def cd(command, err_file):
    params = command.split()[1:]
    path = params[0] if params else os.environ['HOME']

    cmd, *args = command.split()

    pid = os.getpid()

    try:
        os.chdir(path)

        lines = 0
        returncode = 0
        return cmd, args, lines, pid, returncode
    except OSError as e:
        print(e, end="", file=err_file)

        lines = 0
        returncode = 1
        return cmd, args, lines, pid, returncode


def run_system(command, err_file):
    p = subprocess.Popen(command, shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         universal_newlines=True)
    stdout, stderr = p.communicate()
    print(stderr, end="", file=err_file)
    print(stdout, end="")

    time = strftime("[%Y-%m-%d %H:%M:%S]", localtime())
    cmd, *args = command.split()
    lines = len(stdout.split('\n'))
    pid = p.pid
    returncode = p.returncode

    return cmd, args, lines, pid, returncode


def myshell_run():
    with open("myshell.log", "a") as log_file:
        with open("myshell.err", "a") as err_file:
            while True:
                try:
                    command = input(f"myshell [{get_short_path()}]: ")
                    if command.startswith("cd ") or command == "cd":
                        run_log(lambda: cd(command, err_file), log_file)
                        continue
                    if command == "exit":
                        break
                    run_log(lambda: run_system(command, err_file), log_file)
                except EOFError:
                    break
            myshell_exit()


if __name__ == '__main__':
    myshell_run()
