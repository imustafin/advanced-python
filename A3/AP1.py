# Python 3.8.3

import inspect

def reflect(f):
    """
    No. Quine needs to print the whole source of the whole program
    not of just one function.
    """
    def ff(*args, **kwargs):
        s = inspect.getsource(f)
        if s.startswith('@'):
            s = '\n'.join(s.split('\n')[1:])
        print(s)

    return ff


@reflect
def foo():
    print('bar')

if __name__ == '__main__':
    foo()
