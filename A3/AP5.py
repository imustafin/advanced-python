# Python 3.8.3

from reflect import reflect

@reflect
def myfunction():
    print('nothing\nuseful')

myfunction()

# We can't write `@reflect` before `def reflect` because it is not defined
# before `def`. But we can call decorator functions ourselves and get
# a decorated function like this:
decorated_reflect = reflect(reflect)
decorated_reflect(print)
