from repyrts_ap3 import stat_object, stat_complexity, report_object, report_complexity

@report_object
@report_complexity
def foo():
    print('hello')

if __name__ == '__main__':
    foo()
