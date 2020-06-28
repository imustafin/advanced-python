### Python Programming for Software Engineers
### Assignment 7
### 'Lambda De Parser'


# [Ilgiz Mustafin, Valeria Yurinskaya]

# Task 1
# ----------------------------------------------
# Given the following:
f = lambda x, y: x * y


# 1. Rewrite to its logical equivalence using ordinary funcion definition(s)

def f(x, y):
    return x * y

# Task 2
# ----------------------------------------------
# Given the following:
f = lambda x: (lambda y: (lambda z: x + y + z))

# 1. How would you call it to get the result of `x + y + z`?

# suppose x, y, z = 9, 2, 3
f(9)(2)(3)

# 2. Rewrite it using only one lambda expression and show how to call it

f = lambda x, y, z: x + y + z
f(9, 2, 3)

# Task 3
# ----------------------------------------------
# Given the following:
(lambda b=(lambda *c: print(c)): b("a", "b"))()


# 1. What happens here? Rewrite it so that the code can be
# understood by a normal or your mate who has no idea what the lambda is!
# Provide comments, neat formatting and a bit more meaningful var names.


def print_args(*args):
    return print(args)

# In the original form
# (lambda b=(lambda *c: print(c)): b("a", "b"))()
# (lambda b=(lambda *c: print(c)): b("a", "b")) - is a lambda function F with one argument b
# we rewrote F(b) as main_function(function)
def main_function(function=print_args):
    """call the given function with arguments ('a', 'b')"""
    return function("a", "b")


main_function()  # use default function print_args
main_function(zip)  # use passed function zip


# Task 4 (soft)
# ----------------------------------------------
# What are the main restrictions on the lambda?
# Provide "If yes, why? If not, why not?" for each of the following:
# 1. Does lambda restrict side effects?
# 2. Does lambda restrict number of allowed statements?
# 3. Does lambda restrict assignments?
# 4. Does lambda restrict number of return values?
# 5. Does lambda restrict the use of default arguments values?
# 6. Does lambda restrict possible function signatures?

# Answers
# 1. No. Lambda expressions can call functions which can have side effects.
# 2. Lambda allows only one expression, not statement. It is done by the language.
# 3. Assignments are not allowed in lambdas but calls which effectively assign something are allowed.
# 4. Value of the given expression is returned, additional return statements are not allowed.
# 5. No, parameters can have default values like lambda x=2: x + 1.
# 6. No, lambda can have any signature allowed for functions.

# Task 5
# ----------------------------------------------
# Given the following:
(lambda f=(lambda a: (lambda b: print(list(map(lambda x: x + x, a + b))))):
 f((1, 2, 3))((4, 5, 6)))()

# 1. What happens here? Do the same as in Task 3 and
# enumerate order of execution using (1,2,3...) in comments
# [multiline code interlaced with comments]

def default_of_a(a):
    def default_of_b(b):  # 3
        def map_f(x):  # 5
            return x + x  # 7
        print(list(map(map_f, a + b)))  # 6

    return default_of_b  # 4

def outer(f=default_of_a):
    return f((1, 2, 3))((4, 5, 6))  # 2

outer()  # 1

# 2. Why does map() requires list() call?
# [written answer]
# map itself does not require the list call. Here list was probably used
# to run the computation for the whole (a + b) iterable and to get result
# as printable list.
