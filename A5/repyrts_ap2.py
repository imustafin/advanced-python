# Python 3.8.3

import ast
import contextlib
import inspect
import io
import math
import string
import sys
import tokenize
import textwrap

def stat_object(f):
    """
    No. Quine needs to print the whole source of the whole program
    not of just one function.
    """
    def ff(*args, **kwargs):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            f(*args, **kwargs)

        print({
            'name': f.__name__,
            'type': type(f),
            'sign': str(inspect.signature(f)),
            'args': f'positional {args}\nkey=worded {kwargs}',
            'doc': inspect.cleandoc(f.__doc__ or 'None'),
            'source': inspect.getsource(f),
            'output': out.getvalue()
        })

    return ff


class Analyzer(ast.NodeVisitor):
    '''Count different stats for the code'''

    def __init__(self):
        self.stats = {}

        self.operands = {}

    def found(self, op):
        if op not in self.stats:
            self.stats[op] = 0
        self.stats[op] += 1

    def operand(self, s):
        if s not in self.operands:
            self.operands[s] = 0
        self.operands[s] += 1

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

    def visit_IfExp(self, node):
        self.found('if')
        self.found('else')

        self.generic_visit(node)


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
        self.operand('entities')

        if ast.get_docstring(node):
            self.operand('docstrings')

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

        for a in node.args:
            self.operand('args')

        for a in node.keywords:
            self.operand('args')

        self.generic_visit(node)

    def visit_Index(self, node):
        self.operand('args')

    def visit_Slice(self, node):
        if node.lower:
            self.operand('args')

        if node.upper:
            self.operand('args')

        if node.step:
            self.operand('args')


    def visit_Assign(self, node):
        self.found('assignment')
        self.operand('entities')

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

    def visit_Not(self, node):
        self.found('logic')

        self.generic_visit(node)


    def visit_ClassDef(self, node):
        self.operand('entities')

        if ast.get_docstring(node):
            self.operand('docstrings')

        self.generic_visit(node)

    def visit_Module(self, node):
        if ast.get_docstring(node):
            self.operand('docstrings')

        self.generic_visit(node)

    def visit_Constant(self, node):
        self.operand('literals')


        self.generic_visit(node)

    def visit_FormattedValue(self, node):
        self.operand('literals')


        self.generic_visit(node)

    def visit_JoinedStr(self, node):
        self.operand('literals')


        self.generic_visit(node)

    def visit_List(self, node):
        self.operand('literals')

        self.generic_visit(node)

    def visit_Tuple(self, node):
        self.operand('literals')

        self.generic_visit(node)

    def visit_Set(self, node):
        self.operand('literals')

        self.generic_visit(node)

    def visit_Dict(self, node):
        self.operand('literals')

        self.generic_visit(node)


    def visit_comprehension(self, node):
        for f in node.ifs:
            self.found('if')


def report(operators, operands):
    operators_report = {}
    words = [
        'if', 'elif', 'else', 'try', 'for', 'with', 'return',
        'def', 'import', 'except', 'calls', 'arithmetic',
        'logic', 'assignment'
    ]

    n1 = 0
    N1 = 0

    for k in words:
        if k in operators and operators[k]:
            operators_report[k] = operators[k]
            n1 += 1
            N1 += operators[k]
        else:
            operators_report[k] = 0

    operators_report['N1'] = N1

    operands_report = {}

    operand_words = [
        'docstrings', 'inlinedocs', 'literals', 'entities', 'args'
    ]

    n2 = 0
    N2 = 0

    for k in operand_words:
        if k in operands and operands[k]:
            operands_report[k] = operands[k]
            n2 += 1
            N2 += operands[k]
        else:
            operands_report[k] = 0

    operands_report['N2'] = N2

    program_report = {}

    n = n1 + n2
    program_report['vocabulary'] = n

    N = N1 + N2
    program_report['length'] = N

    try:
        CL = n1 * math.log2(n1) + n2 * math.log2(n2)
    except ValueError:
        CL = math.nan

    program_report['calc_length'] = CL

    try:
        V = N * math.log2(n)
    except ValueError:
        V = math.nan

    program_report['volume'] = V

    try:
        D = n1/2 * N2/n2
    except ValueError:
        D = math.nan

    program_report['difficulty'] = D

    program_report['effort'] = D * V

    print({
        'operators': operators_report,
        'operands': operands_report,
        'program': program_report
    })
        
def stat_complexity(f):
    code = textwrap.dedent(inspect.getsource(f))

    tree = ast.parse(code)

    analyzer = Analyzer()
    analyzer.visit(tree)

    stats = analyzer.stats
    operands = analyzer.operands

    # Add comments
    tokens = tokenize.generate_tokens(io.StringIO(code).readline)

    comments = list(filter(lambda x: x.type == tokenize.COMMENT, tokens))
    comments_count = len(comments)
    operands['inlinedocs'] = comments_count

    # Docstrings are actually literals but we count them separately
    if 'literals' in operands and 'docstrings' in operands:
        operands['literals'] -= operands['docstrings']

    report(stats, operands)

    return f
