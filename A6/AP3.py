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
# letter -> lower-case latin

EXPRS = []

class Value:
    def __init__(self, coef, s, exponention):
        self.coef = coef
        self.s = s
        self.exponention = exponention

    def term_op(self, other, do_plus):
        assert self.s == other.s and self.exponention == other.exponention

        if do_plus:
            c = self.coef + other.coef
        else:
            c = self.coef - other.coef

        return Value(self.coef + other.coef, self.s, self.exponention)

    def sum(self, other):
        return self.term_op(other, True)

    def sub(self, other):
        print(self, '-', other)
        return self.term_op(other, False)

    def factor_op(self, other, do_mult):
        assert self.s == other.s

        if do_mult:
            return Value(self.coef * other.coef, self.s, self.exponention + other.exponention)
        return Value(self.coef / other.coef, self.s, self.exponention - other.exponention)
            
    def mult(self, other):
        return self.factor_op(other, True)

    def div(self, other):
        return self.factor_op(other, False)


    def __repr__(self):
        s = ''

        if self.coef != 1:
            s += str(self.coef)

        if self.coef == 1 and not self.s:
            s += str(self.coef)

        s += self.s

        if self.exponention != 1:
            s += '^' + str(self.exponention)

        return s

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
            return lc.sum(rc)
        elif self.op == '-':
            return lc.sub(rc)
        elif self.op == '*':
            return lc.mult(rc)
        elif self.op == '/':
            return lc.div(rc)
        else:
            raise NotImplementedError()

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
        return Value(int(self.s), '', 1)

class NameNode(Node):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    def compute(self):
        return Value(1, self.name, 1)

class ParensNode(Node):
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f'({self.expr})'

    def compute(self):
        val = self.expr.compute()
    
        return Value(1, f'({val.s})', 1)

class SquaresNode(Node):
    def __init__(self, integer):
        self.integer = integer

    def __repr__(self):
        return f'[{self.integer}]'

    def compute(self):
        index = self.integer.compute().coef
        val = EXPRS[index].compute()
        
        return val

    
class CoefficientedNode(Node):
    def __init__(self, coef, coefficiented):
        self.coef = coef
        self.coefficiented = coefficiented

    def __repr__(self):
        return f'<CF {self.coef} {self.coefficiented}>'

    def compute(self):
        if self.coef:
            raise NotImplementedError()

        return self.coefficiented.compute()

# All parse_* return (Node, String)

def take_any_char(s, chars):
    if s and s[0] in chars:
        return s[0], s[1:]
    raise ApParseError(s, chars)

def take_one_or_more(s, chars):
    ans, ss = take_any_char(s, chars)

    while True:
        try:
            next_c, ss = take_any_char(ss, chars)
            ans += next_c
        except ApParseError:
            # no more digits
            break

    return ans, ss


def parse_integer(s):
    digits = '0123456789'

    integer, ss = take_one_or_more(s, digits)
        
    return IntegerNode(integer), ss

def parse_name(s):
    letters = 'abcdefghijklmnopqrstuvwxyz'

    ans, ss = take_one_or_more(s, letters)

    return NameNode(ans), ss

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

    try:
        return parse_name(s)
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

            if command.startswith('expand'):
                command = command.split()[-1]

            do_expression(command)

        except EOFError:
            break
        except ApParseError:
            print(command)
            print('err: invalid expression')
            traceback.print_exc()
    

if __name__ == '__main__':
    main()
