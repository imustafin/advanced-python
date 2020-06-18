import ast
import sys

class Analyzer(ast.NodeVisitor):
    def __init__(self):
        self.stats = {}

    def found(self, op):
        if op not in self.stats:
            self.stats[op] = 0
        self.stats[op] += 1

    def visit_Expr(self, node):
        self.generic_visit(node)

    def visit_If(self, node, elsif=False):
        if elsif:
            self.found('elsif')
        else:
            self.found('if')

        self.visit(node.test)

        if node.body:
            for b in node.body:
                self.visit(b)

        else_found = False
        if node.orelse:
            for orelse in node.orelse:
                if isinstance(orelse, ast.If):
                    self.visit_If(orelse, True)
                else:
                    else_found = True
                    self.visit(orelse)

        if else_found:
            self.found('else')

    def visit_Try(self, node):
        self.found('try')

        for b in node.body:
            self.generic_visit(b)

        if node.handlers:
            for h in node.handlers:
                self.visit(h)

        if node.orelse:
            for orelse in node.orelse:
                self.found('else')
                self.visit(orelse)

        if node.finalbody:
            for finalbody in node.finalbody:
                self.visit(finalbody)

    def visit_ExceptHandler(self, node):
        self.found('except')

        self.generic_visit(node)

    def visit_For(self, node):
        self.found('for')

        self.visit(node.target)

        self.visit(node.iter)

        for b in node.body:
            self.visit(b)

        if node.orelse:
            self.found('else')
            for b in node.orelse:
                self.visit(b)

    def visit_AsyncFor(self, node):
        self.visit_For(node)

    def visit_With(self, node):
        self.found('with')

        self.generic_visit(node)

    def visit_AsyncWith(self, node):
        self.visit_With(node)


    def visit_Return(self, node):
        self.found('return')

        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.found('def')

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)


    def visit_Import(self, node):
        self.found('import')

        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        self.visit_Import(node)

    def visit_Call(self, node):
        self.found('call')

        self.generic_visit(node)

    def visit_Assign(self, node):
        self.found('assignment')

        self.generic_visit(node)

    def visit_UAdd(self, node):
        self.found('arithmetic')

        self.generic_visit(node)

    def visit_USub(self, node):
        self.found('arithmetic')

        self.generic_visit(node)

    def visit_Add(self, node):
        self.found('arithmetic')

        self.generic_visit(node)

    def visit_Sub(self, node):
        self.found('arithmetic')

        self.generic_visit(node)

    def visit_Mult(self, node):
        self.found('arithmetic')

        self.generic_visit(node)

    def visit_Div(self, node):
        self.found('arithmetic')

        self.generic_visit(node)

    def visit_And(self, node):
        self.found('logic')

        self.generic_visit(node)

    def visit_Eq(self, node):
        self.found('logic')

        self.generic_visit(node)

    def visit_NotEq(self, node):
        self.found('logic')

        self.generic_visit(node)

    def visit_IsNot(self, node):
        self.found('logic')

        self.generic_visit(node)

    def visit_NotIn(self, node):
        self.found('logic')

        self.generic_visit(node)

    def visit_not(self, node):
        self.found('logic')

        self.generic_visit(node)

    def report(self):
        print('[operators]')
        words = [
            'if', 'elif', 'else', 'try', 'for', 'with', 'return',
            'def', 'import', 'except', 'calls', 'arithmetic',
            'logic', 'assignment'
        ]

        N1 = 0

        for k in words:
            if k in self.stats:
                print(k + ':', self.stats[k])
                N1 += self.stats[k]
        print('N1:', N1)
        
        
def main():
    tree = ast.parse(sys.stdin.read())

    analyzer = Analyzer()
    analyzer.visit(tree)
    analyzer.report()


if __name__ == '__main__':
    main()
