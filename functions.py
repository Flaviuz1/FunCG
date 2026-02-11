import re
import math
from fractions import Fraction

# Token types
NUMBER, IDENT, OP, LPAREN, RPAREN, COMMA = 'NUMBER', 'IDENT', 'OP', 'LPAREN', 'RPAREN', 'COMMA'

SUPPORTED_FUNCTIONS = [
    'sum', 'integral', 'product', 'logarithm', 'absolute', 'factorial',
    'floor', 'ceiling', 'lim',
    'sin', 'cos', 'tan', 'ctg', 'arcsin', 'arccos', 'arctan', 'arcctg'
]

def tokenize(expr : str) -> list:
    token_spec = [
        (NUMBER,  r'\d+(\.\d*)?([eE][+-]?\d+)?'),
        (IDENT,   r'[a-zA-Z_][a-zA-Z0-9_]*'),
        (OP,      r'[\+\-\*/\^=]'),
        (LPAREN,  r'\('),
        (RPAREN,  r'\)'),
        (COMMA,   r','),
        ('SKIP',  r'[ \t]+'),
        ('MISMATCH', r'.'),
    ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_spec)
    get_token = re.compile(tok_regex).match
    pos = 0
    tokens = []
    mo = get_token(expr, pos)
    while mo:
        kind = mo.lastgroup
        value = mo.group()
        if kind == NUMBER:
            tokens.append((NUMBER, float(value)))
        elif kind == IDENT:
            tokens.append((IDENT, value))
        elif kind == OP:
            tokens.append((OP, value))
        elif kind == LPAREN:
            tokens.append((LPAREN, value))
        elif kind == RPAREN:
            tokens.append((RPAREN, value))
        elif kind == COMMA:
            tokens.append((COMMA, value))
        elif kind == 'SKIP':
            pass
        elif kind == 'MISMATCH':
            raise RuntimeError(f'Unexpected character: {value}')
        pos = mo.end()
        mo = get_token(expr, pos)
    return tokens

class ASTNode:
    pass

class NumberNode(ASTNode):
    def __init__(self, value):
        self.value = value

class VariableNode(ASTNode):
    def __init__(self, name):
        self.name = name

class BinaryOpNode(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class FunctionCallNode(ASTNode):
    def __init__(self, func_name, args):
        self.func_name = func_name
        self.args = args

class SigmaSumNode(ASTNode):
    def __init__(self, var, lower, upper, expr):
        self.var = var
        self.lower = lower
        self.upper = upper
        self.expr = expr

class ProductNode(ASTNode):
    def __init__(self, var, lower, upper, expr):
        self.var = var
        self.lower = lower
        self.upper = upper
        self.expr = expr

class IntegralNode(ASTNode):
    def __init__(self, var, lower, upper, expr):
        self.var = var
        self.lower = lower
        self.upper = upper
        self.expr = expr

class LimitNode(ASTNode):
    def __init__(self, var, to, expr):
        self.var = var
        self.to = to
        self.expr = expr

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def advance(self):
        self.pos += 1

    def expect(self, token_type, value=None):
        tok = self.peek()
        if not tok or tok[0] != token_type or (value is not None and tok[1] != value):
            raise SyntaxError(f'Expected {token_type} {value}, got {tok}')
        self.advance()
        return tok

    def parse(self):
        node = self.parse_expression()
        if self.peek() is not None:
            raise SyntaxError('Unexpected token at end')
        return node

    def parse_expression(self):
        node = self.parse_term()
        while self.peek() and self.peek()[0] == OP and self.peek()[1] in ('+', '-'):
            op = self.peek()[1]
            self.advance()
            right = self.parse_term()
            node = BinaryOpNode(node, op, right)
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.peek() and self.peek()[0] == OP and self.peek()[1] in ('*', '/'):
            op = self.peek()[1]
            self.advance()
            right = self.parse_factor()
            node = BinaryOpNode(node, op, right)
        return node

    def parse_factor(self):
        tok = self.peek()
        if tok and tok[1] == '-':
            self.advance()
            return BinaryOpNode(NumberNode(0), '-', self.parse_power())
        return self.parse_power()

    def parse_power(self):
        node = self.parse_atom()
        if self.peek() and self.peek()[1] == '^':
            op = self.peek()[1]
            self.advance()
            right = self.parse_power()
            node = BinaryOpNode(node, op, right)
        return node

    def parse_atom(self):
        tok = self.peek()
        if not tok:
            raise SyntaxError('Unexpected end of input')
        if tok[0] == NUMBER:
            self.advance()
            return NumberNode(tok[1])
        elif tok[0] == IDENT:
            name = tok[1]
            self.advance()
            if self.peek() and self.peek()[0] == LPAREN:
                self.advance()
                args = self.parse_arguments()
                self.expect(RPAREN)
                if name == 'sum':
                    if len(args) != 4:
                        raise SyntaxError('sum expects 4 arguments: var, lower, upper, expr')
                    return SigmaSumNode(args[0].name if isinstance(args[0], VariableNode) else args[0], args[1], args[2], args[3])
                elif name == 'product':
                    if len(args) != 4:
                        raise SyntaxError('product expects 4 arguments: var, lower, upper, expr')
                    return ProductNode(args[0].name if isinstance(args[0], VariableNode) else args[0], args[1], args[2], args[3])
                elif name == 'integral':
                    if len(args) != 4:
                        raise SyntaxError('integral expects 4 arguments: var, lower, upper, expr')
                    return IntegralNode(args[0].name if isinstance(args[0], VariableNode) else args[0], args[1], args[2], args[3])
                elif name == 'lim':
                    if len(args) != 3:
                        raise SyntaxError('limit expects 3 arguments: var, to, expr')
                    return LimitNode(args[0].name if isinstance(args[0], VariableNode) else args[0], args[1], args[2])
                else:
                    return FunctionCallNode(name, args)
            else:
                return VariableNode(name)
        elif tok[0] == LPAREN:
            self.advance()
            node = self.parse_expression()
            self.expect(RPAREN)
            return node
        else:
            raise SyntaxError(f'Unexpected token: {tok}')

    def parse_arguments(self):
        args = []
        while True:
            arg = self.parse_expression()
            args.append(arg)
            tok = self.peek()
            if tok and tok[0] == COMMA:
                self.advance()
                continue
            else:
                break
        return args

ISPTCPrecision = 1000
ESCPrecision = 100

def evaluate(node, variables=None):
    if variables is None:
        variables = {}
    if isinstance(node, NumberNode):
        return node.value
    elif isinstance(node, VariableNode):
        constants = {'pi': math.pi, 'e': math.e, 'inf': 1e8}
        lname = node.name.lower()
        if lname in variables:
            return variables[lname]
        elif lname in constants:
            return constants[lname]
        else:
            raise ValueError(f"Variable '{node.name}' not defined")
    elif isinstance(node, BinaryOpNode):
        left = evaluate(node.left, variables)
        right = evaluate(node.right, variables)
        if node.op == '+':
            return left + right
        elif node.op == '-':
            return left - right
        elif node.op == '*':
            return left * right
        elif node.op == '/':
            return left / right
        elif node.op == '^':
            return power(left, right)
        else:
            raise ValueError(f"Unknown operator: {node.op}")
    elif isinstance(node, FunctionCallNode):
        args = [evaluate(arg, variables) for arg in node.args]
        fname = node.func_name.lower()
        trig_funcs = {
            'sin': sin, 'cos': cos, 'tg': tg, 'ctg' : ctg,
            'arcsin': arcsin, 'arccos': arccos, 'arctg': arctg, 'arcctg' : arcctg
        }
        if fname in trig_funcs:
            return trig_funcs[fname](*args)
        elif fname == 'logarithm':
            if len(args) == 1:
                return logarithm(math.e, args[0])
            elif len(args) == 2:
                return logarithm(args[0], args[1])
            else:
                raise ValueError('logarithm expects 1 or 2 arguments')
        elif fname == 'absolute':
            return absolute(args[0])
        elif fname == 'factorial':
            return factorial(int(args[0]))
        elif fname == 'floor':
            return floor(args[0])
        elif fname == 'ceiling':
            return ceiling(args[0])
        else:
            raise ValueError(f"Unknown function: {fname}")
    elif isinstance(node, SigmaSumNode):
        var = node.var
        lower = int(evaluate(node.lower, variables))
        upper = int(evaluate(node.upper, variables))
        total = 0
        for i in range(lower, upper + 1):
            variables[var] = i
            total += evaluate(node.expr, variables)
        del variables[var]
        return total
    elif isinstance(node, ProductNode):
        var = node.var
        lower = int(evaluate(node.lower, variables))
        upper = int(evaluate(node.upper, variables))
        prod = 1
        for i in range(lower, upper + 1):
            variables[var] = i
            prod *= evaluate(node.expr, variables)
        del variables[var]
        return prod
    elif isinstance(node, IntegralNode):
        var = node.var
        a = evaluate(node.lower, variables)
        b = evaluate(node.upper, variables)
        n = ISPTCPrecision
        # Simpson's Rule
        if n % 2 == 1:
            n += 1
        h = (b - a) / n
        total = 0.0
        for i in range(n + 1):
            x = a + i * h
            variables[var] = x
            f = evaluate(node.expr, variables)
            if i == 0 or i == n:
                total += f
            elif i % 2 == 1:
                total += 4 * f
            else:
                total += 2 * f
        del variables[var]
        return total * h / 3
    elif isinstance(node, LimitNode):
        var = node.var
        if not isinstance(var, str):
            raise ValueError("First argument to limit must be a variable name")
        to = evaluate(node.to, variables)
        eps = 1e-6
        try:
            variables[var] = to - eps
            left = evaluate(node.expr, variables)
            variables[var] = to + eps
            right = evaluate(node.expr, variables)
        finally:
            if var in variables:
                del variables[var]
        if abs(left - right) < 1e-4 and all(map(lambda v: abs(v) < 1e10, [left, right])):
            return (left + right) / 2
        else:
            raise ValueError("Limit does not exist (left/right limits differ)")
    else:
        raise ValueError(f"Unknown AST node: {type(node)}")

# Math functions
factorialsmemo = {0 : 1, 1 : 1}
def factorial(x : int) -> int:
    if x in factorialsmemo:
        return factorialsmemo[x]
    last = max(factorialsmemo)
    ans = factorialsmemo[last]
    for i in range(last + 1, x + 1):
        ans *= i
        factorialsmemo[i] = ans
    return ans

def absolute(x : float) -> float:
    return -x if x < 0 else x

def ceiling(x: float) -> int:
    ans = floor(x)
    if x > ans:
        return ans + 1
    return ans

def floor(x: float) -> int:
    ans = 0
    if x >= 0:
        while ans + 1 <= x:
            ans += 1
    else:
        while ans - 1 >= x:
            ans -= 1
    return ans

def integer(x: float) -> int:
    if x >= 0:
        return floor(x)
    else:
        return ceiling(x)

# Helper function for integer power (no recursion to power())
def _int_power(base, exp):
    """Calculate base^exp where exp is a non-negative integer"""
    result = 1.0
    for _ in range(exp):
        result *= base
    return result

# FIXED logarithm function using Taylor series
def logarithm(b : float, x : float) -> float:
    if x <= 0:
        raise ValueError("logarithm undefined for x <= 0")
    
    if b == math.e:
        if x == 1:
            return 0.0
        if 0.5 <= x <= 1.5:
            t = x - 1
            result = 0.0
            for n in range(1, ESCPrecision + 1):
                sign = 1 if (n + 1) % 2 == 0 else -1
                t_power = _int_power(t, n)
                term = sign * t_power / n
                result += term
            return result
        elif x > 1.5:
            return 1 + logarithm(math.e, x / math.e)
        else:
            return -logarithm(math.e, 1/x)
    else:
        return logarithm(math.e, x) / logarithm(math.e, b)

# FIXED power function
def power(b : float, p : float) -> float:
    if b == 1:
        return 1.0
    elif p == 0:
        return 1.0
    elif b == 0:
        if p > 0:
            return 0.0
        else:
            raise ValueError("0^(negative power) is undefined")
    
    # Integer powers - use repeated multiplication
    if p == integer(p):
        ans = 1.0
        exp = int(abs(p))
        base = b if p > 0 else 1/b
        for _ in range(exp):
            ans *= base
        return ans
    
    # Negative base with non-integer exponent
    if b < 0:
        raise ValueError("Negative base with non-integer exponent")
    
    # For e^p, use Taylor series: e^p = sum(p^n / n!)
    if b == math.e:
        result = 0.0
        for i in range(ESCPrecision + 1):
            p_power = _int_power(p, i)
            result += p_power / factorial(i)
        return result
    
    # For general b^p where b > 0, use: b^p = e^(p * ln(b))
    if b > 0:
        return power(math.e, p * logarithm(math.e, b))
    
    raise ValueError(f"Cannot compute power({b}, {p})")

# Trigonometric functions
def sin(x : float) -> float:
    x = x % (2 * math.pi)
    if x > math.pi:
        x -= 2 * math.pi
    elif x < -math.pi:
        x += 2 * math.pi
    x2 = x*x
    return x * (1 - x2 * (1/6 - x2 * (1/120 - x2 * (1/5040 - x2 * (1/362880 - x2 * (1/39916800))))))

def cos(x : float) -> float:
    x = x % (2 * math.pi)
    if x > math.pi:
        x -= 2 * math.pi
    elif x < -math.pi:
        x += 2 * math.pi

    x2 = x * x
    return 1 - x2 * (1/2 - x2 * (1/24 - x2 * (1/720 - x2 * (1/40320 - x2 * (1/3628800)))))

def tg(x : float) -> float:
    s = sin(x)
    c = cos(x)
    if abs(c) < 1e-10:
        raise ValueError("tangent undefined (cos(x) ≈ 0)")
    return s / c

def ctg(x : float) -> float:
    s = sin(x)
    c = cos(x)
    if abs(s) < 1e-10:
        raise ValueError("cotangent undefined (sin(x) ≈ 0)")
    return c / s

# Inverse trigonometric functions
def arcsin(x: float) -> float:
    if abs(x) > 1:
        raise ValueError("arcsin undefined for abs(x) > 1")
    x2 = x * x
    return x * (1 + x2 * (1/6 + x2 * (3/40 + x2 * (5/112 + x2 * (35/1152 + x2 * 63/2816)))))

def arccos(x : float) -> float:
    return math.pi / 2 - arcsin(x)

def arctg(x: float) -> float:
    if x < 0:
        return -arctg(-x)
    # Coefficients for minimax rational approximation on [0, 0.66]
    P = [
        -8.750608600031904122785e-01,
        -1.615753718733365076637e+01,
        -7.500855792314704667340e+01,
        -1.228866684490136173410e+02,
        -6.485021904942025371773e+01,
    ]

    Q = [
        2.485846490142306297962e+01,
        1.650270098316988542046e+02,
        4.328810604912902668951e+02,
        4.853903996359136964868e+02,
        1.945506571482613964425e+02,
    ]
    if x <= 0.66:
        z = x * x
        num = (((P[0]*z + P[1])*z + P[2])*z + P[3])*z + P[4]
        den = ((((z + Q[0])*z + Q[1])*z + Q[2])*z + Q[3])*z + Q[4]
        return x + x * z * num / den
    if x <= 2.414213562373095:  # 1 + sqrt(2)
        return math.pi/4 + arctg((x - 1) / (x + 1))
    return math.pi/2 - arctg(1/x)

def arcctg(x : float) -> float:
    return math.pi / 2 - arctg(x)
