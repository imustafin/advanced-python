# Python 3.7.5

import sys
import dis
import marshal
import types


def print_usage():
    print('usage: AP3.py FORMAT SRC \n'
          '-py src.py      produce human-readable bytecode from python file \n'
          '-pyc src.pyc    produce human-readable bytecode from compiled .pyc file \n'
          '-s src        produce human-readable bytecode from normal string')


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
    elif format == '-pyc':
        with open(src, 'br') as file:
            file.seek(16)  # depends on compiler version
            source = marshal.load(file)
    elif format == '-s':
        source = src
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