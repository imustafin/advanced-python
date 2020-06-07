# Python 3.7.5

import sys
import dis
import types


def print_usage():
    print('usage: AP2.py -py FILE_NAME')


def print_row(ar, width=13):
    format_string = ' | '.join([f'{{:{width}.{width}}}'] * len(ar))
    print(format_string.format(*map(str, ar)))


def recursive_dis(x):
    for op in dis.get_instructions(x):
        yield op
        if isinstance(op.argval, types.CodeType):
            yield from recursive_dis(op.argval)


def get_bytecode(format, src):
    if format == '-py':
        with open(src, 'r') as file:
            source = file.read()
    else:
        raise Exception('No such format ' + format)

    return recursive_dis(source)


def main():
    args = sys.argv[1:]

    if len(args) != 2:
        print_usage()
        return

    bc = get_bytecode(args[0], args[1])

    for x in bc:
        print_row([x.opname, x.argrepr])


if __name__ == '__main__':
    main()