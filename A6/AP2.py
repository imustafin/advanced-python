# Python 3.8.3

import traceback
import textwrap


# EXPRESSION SYNTAX
#
# expression -> term
# term -> factor { _ term_op _ factor }
# term_op -> ("+" | "-")
# factor -> combined { _ factor_op _ combined }
# factor_op -> ("*" | "/")
# combined -> [term_op] (coefficiented | num) [exponention]
# coefficiented ->  [integer] coefficientable
# coefficientable -> name | "(" expression ")" | "[" integer "]"
# exponention -> "^" integer
# num -> relation | integer
# primary -> num | coefficientable
# relation -> integer "/" integer
# name -> letter+
# _ -> " "

EXPRS = []

class ApParseError(Exception):
    def __init__(self, ss, expected=None, ers=[]):
        msg = '"' + ss + '"'
        if expected:
            msg += ' <--- here expected "' + expected + '"'

        strs = list(map(str, ers))
        lines = '\n'.join(strs)
        ers_msgs = textwrap.indent(lines, '  ')
        msg += '\n' + ers_msgs
        super().__init__(msg)

class Node:
    def compute(self):
        raise NotImplementedError()

class BinaryNode(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return f'<BIN {self.left} {self.op} {self.right}>'

    def compute(self):
        lc = self.left.compute()
        rc = self.right.compute()

        if self.op == '+':
            return lc + rc
        elif self.op == '-':
            return lc - rc
        else:
            super().compute()

class CombinedNode(Node):
    def __init__(self, sign, primary, exponention):
        self.sign = sign 
        self.primary = primary
        self.exponention = exponention

    def __repr__(self):
        return f'<CMB {self.sign} {self.primary} {self.exponention}>'

    def compute(self):
        val = self.primary.compute()

        if self.sign == '-':
            val = -val

        if self.exponention:
            super().compute()

        return val

class IntegerNode(Node):
    def __init__(self, s):
        self.s = s

    def __repr__(self):
        return self.s

    def compute(self):
        return int(self.s)

class ParensNode(Node):
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f'({self.expr})'

    def compute(self):
        return self.expr.compute()

class SquaresNode(Node):
    def __init__(self, integer):
        self.integer = integer

    def __repr__(self):
        return f'[{self.integer}]'

    def compute(self):
        return EXPRS[self.integer.compute()].compute()
    
class CoefficientedNode(Node):
    def __init__(self, coef, coefficiented):
        self.coef = coef
        self.coefficiented = coefficiented

    def __repr__(self):
        return f'<CF {self.coef} {self.coefficiented}>'

    def compute(self):
        if self.coef:
            super().compute()

        return self.coefficiented.compute()

# All parse_* return (Node, String)

def take_any_char(s, chars):
    if s and s[0] in chars:
        return s[0], s[1:]
    raise ApParseError(s, chars)

def parse_integer(s):
    digits = '0123456789'

    ans, ss = take_any_char(s, digits)

    while True:
        ss_before_try = ss
        try:
            next_digit, ss = take_any_char(ss, digits)
            ans += next_digit
        except ApParseError:
            # no more digits
            break
        

    return IntegerNode(ans), ss_before_try

def parse_parens(s):
    _, ss = take_any_char(s, '(')

    expr, ss = parse_expression(ss)

    _, ss = take_any_char(ss, ')')

    return ParensNode(expr), ss

def parse_num(s):
    return parse_integer(s)

def parse_squares(s):
    _, ss = take_any_char(s, '[')

    integer, ss = parse_integer(ss)

    _, ss = take_any_char(ss, ']')

    return SquaresNode(integer), ss

def parse_coefficientable(s):
    ers = []

    try:
        return parse_parens(s)
    except ApParseError as e:
        ers.append(e)
        pass

    try:
        return parse_squares(s)
    except ApParseError as e:
        ers.append(e)
        pass

    raise ApParseError(s, 'coefficientable', ers)

def parse_primary(s):
    try:
        return parse_num(s)
    except ApParseError:
        pass

    try:
        return parse_coefficientable(s)
    except ApParseError:
        pass

    raise ApParseError(s, 'primary')

def parse_exponention(s):
    _, ss = take_any_char(s, '^')
    return parse_integer(ss)


def parse_coefficiented(s):
    ss = s

    coef = None
    try:
        coef, ss = parse_integer(ss)
    except:
        # no coef
        pass

    coefficientable, ss = parse_coefficientable(ss)

    return CoefficientedNode(coef, coefficientable), ss

def parse_combined(s):
    ss = s

    sign = None
    try:
        sign, ss = parse_term_op(ss)
    except ApParseError:
        # no sign
        pass

    ers = []

    body = None
    try:
        body, ss = parse_coefficiented(ss)
    except ApParseError as e:
        ers.append(e)
        pass

    if not body:
        try:
            body, ss = parse_num(ss)
        except ApParseError as e:
            ers.append(e)
            raise ApParseError(ss, 'coefficiented or num', ers) from ers[0]

    exponention = None
    try:
        exponention, ss = parse_exponention(ss)
    except ApParseError:
        # no exponention
        pass

    return CombinedNode(sign, body, exponention), ss



def parse_factor_op(s):
    return take_any_char(s, '*/')

def parse_factor(s):
    node, ss = parse_combined(s)

    while True:
        old_ss = ss
        try:
            _, ss = parse_space(ss)

            op, ss = parse_factor_op(ss)
        except ApParseError:
            # no more combineds
            ss = old_ss
            break

        _, ss = parse_space(ss)

        right, ss = parse_combined(ss)

        node = BinaryNode(node, op, right)

    return node, ss


def parse_space(s):
    return take_any_char(s, ' ')

def parse_term_op(s):
    return take_any_char(s, '+-')

def parse_term(s):
    node, ss = parse_factor(s)

    while True:
        old_ss = ss
        try:
            _, ss = parse_space(ss)

            op, ss = parse_term_op(ss)
        except ApParseError:
            # no more terms
            ss = old_ss
            break

        _, ss = parse_space(ss)

        right, ss = parse_factor(ss)

        node = BinaryNode(node, op, right)

    return node, ss



def parse_expression(s):
    return parse_term(s)


def do_expression(s):
    tree, ss = parse_expression(s.strip())

    if ss:
        raise ApParseError(ss, 'END')

    EXPRS.append(tree)

    print(f'{len(EXPRS) - 1}:', tree.compute())


def main():
    while True:
        try:
            command = input('>>> ')
            if not command:
                continue

            if command == 'exit':
                break

            do_expression(command)

        except EOFError:
            break
        except ApParseError:
            # print(command)
            print('err: invalid expression')
            # traceback.print_exc()
    

if __name__ == '__main__':
    main()
