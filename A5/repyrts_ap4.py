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
import numpy as np

from fpdf import FPDF

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt

class PDF(FPDF):
    def footer(self):
        # Go to 1.5 cm from bottom
        self.set_y(-15)
        # Select Arial italic 8
        self.set_font('Arial', '', 8)
        # Print centered page number
        self.cell(0, 10, str(self.page_no()), 0, 0, 'C')

    def load_resource(reason, filename):
        if isinstance(filename, io.BytesIO):
            return filename
        return super().load_resource(reason, filename)


param_multipage = True
param_filename = 'report.pdf'
param_papersize= 'a4'

def rc(multipage=True, filename='report.pdf', papersize='a4'):
    global param_multipage
    global param_filename
    global param_papersize
    param_multipage = multipage
    param_filename = filename
    param_papersize = papersize


def make_pdf():
    return PDF(format=param_papersize.upper())

def plot_dict(d):
    x = list(d.keys())
    y = list(d.values())

    fig, ax = plt.subplots()

    ax.bar(x, y)

    ax.set_facecolor('seashell')
    fig.set_facecolor('floralwhite')
    fig.set_figwidth(12)
    fig.set_figheight(6)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')

    buf.seek(0)

    return buf

report_queue = []

def report_pdf(report_name, report, default_filename):
    global report_queue
    if param_multipage:
        report_queue.append((report_name, report))
    else:
        report_queue = [(report_name, report)]



    pdf = make_pdf()
    for report_name, report in report_queue:
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.write(40, report_name)
        pdf.ln()

        for k, v in report.items():
            pdf.set_font('Arial', '', 12)

            pdf.write(5, k)
            pdf.ln()


            pdf.set_font('Courier', '', 10)
            if isinstance(v, dict):
                plot_img = plot_dict(v)
                pdf.image(plot_img, w=200, type='png')
            else:
                pdf.write(5, str(v))
            pdf.ln(10)

    filename = param_filename if param_multipage else default_filename
    pdf.output(filename, 'F')
    


def decorate_object(f, to_pdf, ignore_fields):
    def ff(*args, **kwargs):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            f(*args, **kwargs)

        name = f.__name__
        report = {
            'name': name,
            'type': type(f),
            'sign': str(inspect.signature(f)),
            'args': f'positional {args}\nkey=worded {kwargs}',
            'doc': inspect.cleandoc(f.__doc__ or 'None'),
            'source': inspect.getsource(f),
            'output': out.getvalue()
        }

        report_keys = list(report.keys())
        for k in report_keys:
            if k in ignore_fields and ignore_fields[k] == False:
                del report[k]

        if to_pdf:
            report_pdf(f'{name} Object Report', report, f'{name}_object.pdf')
        else:
            print(report)

    return ff


def report_object(**ignore_fields):
    return lambda x: decorate_object(x, True, ignore_fields)

def stat_object(f):
    return lambda x: decorate_object(x, False, ignore_fields)


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


def complexity_report(operators, operands):
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

    return {
        'operators': operators_report,
        'operands': operands_report,
        'program': program_report
    }
        
def decorate_complexity(f, to_pdf, ignore_fields):
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

    report = complexity_report(stats, operands)

    report_keys = list(ignore_fields.keys())
    for k in report_keys:
        if k in ignore_fields:
            if ignore_fields[k] == False:
                del report[k]

    name = f.__name__
    if to_pdf:
        report_pdf(f'{name}Complexity Report', report, f'{name}_complexity.pdf')
    else:
        print(report)

    return f

def stat_complexity(**ignore_fields):
    return lambda x: decorate_complexity(x, False, ignore_fields)

def report_complexity(**ignore_fields):
    return lambda x: decorate_complexity(x, True, ignore_fields)
