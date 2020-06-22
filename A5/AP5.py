from repyrts_ap5 import stat_object, stat_complexity, report_object, report_complexity, rc, Analyzer

rc(multipage=True, filename='reports.pdf', papersize='a4')

@report_object(output=False)
@report_complexity(operands=False)
class Foo:

    def hello(self):
        print('hello')

if __name__ == '__main__':
    Foo().hello()
    report_object(source=False)(report_complexity()(Analyzer))
