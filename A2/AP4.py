# Python 3.7.5

import sys
import dis
import marshal
from pathlib import Path
import types
import py_compile
import tempfile


def print_bytecode(source):
    bc = dis.Bytecode(source)
    for x in bc:
        print_row([x.opname, x.argrepr])


def print_usage():
    print('usage: AP4.py ACTION [FORMAT SRC] \n'
          'compile \n'
                '-py file.py     compile file into bytecode and store it as file.pyc \n'
                '-s "src"        compile src into bytecode and store it as out.pyc \n'
          'print \n'
                 '-py src.py      produce human-readable bytecode from python file \n'
                 '-pyc src.pyc    produce human-readable bytecode from compiled .pyc file \n'
                 '-s src        produce human-readable bytecode from normal string \n')


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


def program_print(args):
    print_bytecode(get_bytecode(args[1], args[2]))


def program_compile(args):
    if args[1] == '-py':
        source = args[2]
        filename = Path(args[2]).stem + '.pyc'
    elif args[1] == '-s':
        with tempfile.NamedTemporaryFile('w', delete=False) as tmp:
            source = tmp.name
            print(tmp.name)
            tmp.write(args[2])
        filename = 'out.pyc'
    else:
        print_usage()
        return

    py_compile.compile(source, cfile=filename)


def main():
    args = sys.argv[1:]

    if len(args) != 3:
        print_usage()
        return

    if args[0] == 'print':
        program_print(args)
    elif args[0] == 'compile':
        program_compile(args)
    else:
        print_usage()
        return


if __name__ == '__main__':
    main()