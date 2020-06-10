# Python 3.8.3

import inspect
import io
import contextlib
import string
import ast

def print_pairs(pairs, w=9):
    line_format = f'{{:{w}.{w}}}{{}}'
    for k, v in pairs:
        lines = v.split('\n')

        if not lines:
            print(line_format.format(k, ''))
            continue

        print(line_format.format(k, lines[0]))

        for line in lines[1:]:
            print(line_format.format('', line))


def count_ifs(code):
    return len([n for n in ast.walk(ast.parse(code)) if isinstance(n, ast.If)])


def reflect(f):
    """
    No. Quine needs to print the whole source of the whole program
    not of just one function.
    """
    def ff(*args, **kwargs):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            f(*args, **kwargs)

        print_pairs([
            ('Name:', f.__name__),
            ('Type:', str(type(f))),
            ('Sign:', str(inspect.signature(f))),
            ('Args:', f'positional {args}\nkey=worded {kwargs}'),
            ('Doc:', inspect.cleandoc(f.__doc__ or 'None')),
            ('Complx:', str({'if': count_ifs(inspect.getsource(f))})),
            ('Source:', inspect.getsource(f)),
            ('Output:', out.getvalue())
        ])

    return ff
