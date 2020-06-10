# Python 3.8.3

import inspect
import io
import contextlib

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
            ('', ''),
            ('Args:', f'positional {args}\nkey=worded {kwargs}'),
            ('', ''),
            ('Doc:', inspect.cleandoc(f.__doc__ or 'None')),
            ('', ''),
            ('Source:', inspect.getsource(f)),
            ('Output:', out.getvalue())
        ])

    return ff


@reflect
def foo(bar1, bar2=''):
    """
    This function does nothing useful
    :param bar1: description
    :param bar2: description
    """
    print('some\nmultiline\noutput')

if __name__ == '__main__':
    foo(None, bar2='')
