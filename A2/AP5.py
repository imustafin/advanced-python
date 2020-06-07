# Python 3.7.5

import sys
import dis
import marshal
from pathlib import Path
from collections import Counter
import py_compile
import types
import tempfile


def print_bytecode(bc):
    for x in bc:
        print_row([x.opname, x.argrepr])


def print_usage():
    print('usage: AP5.py ACTION [FORMAT SRC] \n'
          'compile \n'
                '-py file.py     compile file into bytecode and store it as file.pyc \n'
                '-s "src"        compile src into bytecode and store it as out.pyc \n'
          'print \n'
                 '-py src.py      produce human-readable bytecode from python file \n'
                 '-pyc src.pyc    produce human-readable bytecode from compiled .pyc file \n'
                 '-s src        produce human-readable bytecode from normal string \n'
          'compare \n'
                 '-format src [-format src]+      produce bytecode comparison for giving sources(supported formats -py, -pyc, -s)')


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


def program_compare(args):
    counts = {}
    ops = set()
    for i in range(1, len(args), 2):
        format, src = args[i:i + 2]

        bc = get_bytecode(format, src)

        opnames = list(map(lambda x: x.opname, bc))
        counts[src] = Counter(opnames)
        ops.update(opnames)

    peaks_sorted = sorted(
        ops,
        key=lambda o: max(map(lambda x: x[o], counts.values())),
        reverse=True
    )

    print_row(['INSTRUCTION', *counts.keys()])
    for op in peaks_sorted:
        print_row([op, *map(lambda x: x[op], counts.values())])


def main():
    args = sys.argv[1:]

    if len(args) < 3:
        print_usage()
        return

    if args[0] == 'print':
        program_print(args)
    elif args[0] == 'compile':
        program_compile(args)
    elif args[0] == 'compare':
        program_compare(args)
    else:
        print_usage()
        return


if __name__ == '__main__':
    main()