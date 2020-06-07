# Python 3.7.5

import sys
import subprocess
import time


def print_row(ar, width=13):
    format_string = ' | '.join([f'{{:{width}.{width}}}'] * len(ar))
    print(format_string.format(*map(str, ar)))


def run_time(file):
    start_time = time.time()

    subprocess.call(
        ["python3", file],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return time.time() - start_time


def main():
    files = sys.argv[1:]

    if not files:
        print("usage: AP1.py [files]")
        return

    with_times_sorted = sorted(zip(files, map(run_time, files)), key=lambda x: x[1])

    print_row(['PROGRAM', 'RANK', 'TIME ELAPSED'])

    for rank, row in enumerate(with_times_sorted):
        print_row([row[0], rank + 1, '{:.5f}s'.format(row[1])])


if __name__ == '__main__':
    main()