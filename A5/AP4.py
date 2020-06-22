from repyrts_ap4 import stat_object, stat_complexity, report_object, report_complexity, rc

rc(multipage=False, filename='report2.pdf', papersize='a4')

@report_object(output=False)
@report_complexity(operands=False)
def foo():
    print('hello')

if __name__ == '__main__':
    foo()
    report_complexity()(report_complexity)
