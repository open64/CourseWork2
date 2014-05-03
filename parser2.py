"""
Separate expression parsing from evaluation by building an explicit parse tree
"""
from _tkinter import create
from copy import deepcopy
from scanner import Scanner, SyntaxError, LexicalError     # from PyTree
import re
from numpy import sin, cos
from math import tan, asin, acos, atan
TraceDefault = False


class UndefinedError(Exception):
    pass


#################################################################################
# the interpreter (a smart objects tree)
#################################################################################


class TreeNode:
    def validate(self, dict_vars):           # default error check
        pass

    def apply(self, dict_vars=dict()):              # default evaluator
        pass

    def is_priority(self, dict_vars):
        pass

    def trace(self, level):             # default unparser
        print('.' * level + '<empty>')

# ROOTS


class BinaryNode(TreeNode):
    def __init__(self, left, right):            # inherited methods
        self.left, self.right = left, right     # left/right branches
        self.label = ''

    def validate(self, dict_vars):
        self.left.validate(dict_vars)                # recurse down branches
        self.right.validate(dict_vars)

    def trace(self, level):
        print('.' * level + '[' + self.label + ']')
        self.left.trace(level+3)
        self.right.trace(level+3)


class PowerNode(BinaryNode):
    label = '^'

    def is_priority(self, dict_vars):
        return self.left.is_priority(dict_vars) or self.right.is_priority(dict_vars)

    def apply(self, dict_vars=dict()):
        return self.left.apply(dict_vars) ** self.right.apply(dict_vars)


class TimesNode(BinaryNode):
    label = '*'

    def is_priority(self, dict_vars):
        return self.left.is_priority(dict_vars) or self.right.is_priority(dict_vars)

    def apply(self, dict_vars=dict()):
        if self.right.is_priority(dict_vars):
            return self.right.apply(dict_vars) * self.left.apply(dict_vars)
        return self.left.apply(dict_vars) * self.right.apply(dict_vars)


class DivideNode(BinaryNode):
    label = '/'

    def is_priority(self, dict_vars):
        return self.left.is_priority(dict_vars) or self.right.is_priority(dict_vars)

    def apply(self, dict_vars=dict()):
        if self.right.is_priority(dict_vars):
            return self.right.apply(dict_vars) / self.left.apply(dict_vars)
        return self.left.apply(dict_vars) / self.right.apply(dict_vars)


class PlusNode(BinaryNode):
    label = '+'

    def is_priority(self, dict_vars):
        return self.left.is_priority(dict_vars) or self.right.is_priority(dict_vars)

    def apply(self, dict_vars=dict()):
        if self.right.is_priority(dict_vars):
            return self.right.apply(dict_vars) + self.left.apply(dict_vars)
        return self.left.apply(dict_vars) + self.right.apply(dict_vars)


class MinusNode(BinaryNode):
    label = '-'

    def is_priority(self, dict_vars):
        return self.left.is_priority(dict_vars) or self.right.is_priority(dict_vars)

    def apply(self, dict_vars=dict()):
        if self.right.is_priority(dict_vars):
            return -self.right.apply(dict_vars) + self.left.apply(dict_vars)
        return self.left.apply(dict_vars) - self.right.apply(dict_vars)

# LEAVES


class NumNode(TreeNode):
    def __init__(self, num):
        self.num = num                 # already numeric

    def apply(self, dict_vars=dict()):             # use default validate
        return self.num

    def trace(self, level):
        print('.' * level + repr(self.num))   # as code, was 'self.num'


class FuncVarNode(TreeNode):
    def __init__(self, name, start, power=1, times=1, plus=0):
        self.name = name                    # variable name
        self.power = power
        self.times = times
        self.plus = plus
        self.column = start                   # column for errors

    def __str__(self):
        string = ''
        if self.times != 1:
            string += str(self.times) + '*'
        var_str = self.str_var()
        if re.search('-|\+|\*|\/|\^', var_str):
            string += '(' + var_str + ')'
        else:
            string += var_str
        if self.power != 1:
            string += '^' + str(self.power)
        if self.plus > 0:
            string += '+' + str(self.plus)
        elif self.plus < 0:
            string += str(self.plus)
        return string

    def __add__(self, other):
        return self._add(other)

    def __radd__(self, other):
        return self._add(other)

    def __sub__(self, other):
        return self._sub(other)

    def __rsub__(self, other):
        return -self._sub(other)

    def __mul__(self, other):
        return self._mul(other)

    def __rmul__(self, other):
        return self._mul(other)

    def __truediv__(self, other):
        if isinstance(other, self.__class__):
            pass
        elif isinstance(other, int) or isinstance(other, float):
            self.times /= other
            self.plus /= other
            return self

    def __rtruediv__(self, other):
        pass

    def __pow__(self, power, modulo=None):
        return self._pow(power)

    def __rpow__(self, power, modulo=None):
        return self._pow(power)

    def __neg__(self):
        self.times = -self.times
        self.plus = -self.plus
        return self

    def __gt__(self, other):
        return self.times > other

    def __lt__(self, other):
        return self.times < other

    def _add(self, other):
        if isinstance(other, self.__class__):
            if self.var == other.var and self.power == other.power:
                self.times += other.times
                self.plus += other.plus
            else:
                self.plus += other
        elif isinstance(other, int) or isinstance(other, float) or isinstance(other, FuncVarNode):
            self.plus += other
        else:
            raise TypeError("unsupported operand type(s) for +: '{}' and '{}'".format(self.__class__, type(other)))
        return self

    def _sub(self, other):
        if isinstance(other, self.__class__):
            if self.var == other.var and self.power == other.power:
                self.times -= other.times
                self.plus -= other.plus
            else:
                self.plus -= other
        elif isinstance(other, int) or isinstance(other, float) or isinstance(other, FuncVarNode):
            self.plus -= other
        else:
            raise TypeError("unsupported operand type(s) for -: '{}' and '{}'".format(self.__class__, type(other)))
        return self

    def _mul(self, other):
        if isinstance(other, self.__class__):
            if self.var == other.var:
                self.power += other.power
            else:
                self.times *= VarNode(other.var, None, other.power)
            self.times *= other.times
            last_plus = self.create_new_mul(self.var, self.power, self.times * other.plus, self.plus * other.plus)
            self.plus = self.create_new_mul(other.var, other.power, other.times * self.plus, last_plus)
        elif isinstance(other, int) or isinstance(other, float) or isinstance(other, FuncVarNode):
            self.times *= other
            self.plus *= other
        else:
            raise TypeError("unsupported operand type(s) for *: '{}' and '{}'".format(self.__class__, type(other)))
        return self

    def _pow(self, power):
        if isinstance(power, self.__class__):
            pass
        elif isinstance(power, int) or isinstance(power, float):
            if self.plus:
                return self.create_new_pow(power)
            else:
                self.times **= power
                self.power *= power
        else:
            raise TypeError("unsupported operand type(s) for *: '{}' and '{}'".format(self.__class__, type(power)))
        return self

    def create_new_pow(self, power):
        pass

    def create_new_mul(self, name, power, times, plus):
        pass

    def str_var(self):
        pass

    def get_var(self, result):
        pass

    def validate(self, dict_vars):
        if not self.name in dict_vars.keys():
            raise UndefinedError(self.name, self.column)

    def apply(self, dict_vars=None):
        if self.name in dict_vars:
            return dict_vars[self.name]
        return self                # validate before apply

    def is_priority(self, dict_vars):
        pass

    def assign(self, value, dict):
        dict[self.name] = value               # local extension

    def trace(self, level):
        print('.' * level + self.name)


class VarNode(FuncVarNode):
    def __init__(self, name, start, power=1, times=1, plus=0):
        FuncVarNode.__init__(self, name, start, power, times, plus)
        self.var = name

    def create_new_pow(self, power):
        return VarNode(self, None, power)

    def create_new_mul(self, name, power, times, plus):
        return VarNode(self.var, None, power, times, plus)

    def str_var(self):
        return str(self.var)

    def get_var(self, result):
        result = ((result-self.plus) / self.times)**(1 / self.power)
        return result, self.var

    def is_priority(self, dict_vars):
        return self.var == dict_vars['_priority']


class FuncNode(FuncVarNode):
    def __init__(self, name, func, arg, power=1, times=1, plus=0, start=None):
        FuncVarNode.__init__(self, name, start, power, times, plus)
        self.func = func
        self.arg = arg

    def create_new_pow(self, power):
        FuncNode(self, self.func, self.arg, power)

    def create_new_mul(self, name, power, times, plus):
        return FuncNode(self.name, self.func, self.arg, power, times, plus)

    def str_var(self):
        return self.name + '(' + str(self.arg) + ')'

    def get_var(self, result):
        result = ((result - self.plus) / self.times)**(1 / self.power)
        if isinstance(result, FuncVarNode):
            result = FuncNode(self.func['reverse_name'], self.func['reverse'], result)
        elif isinstance(result, int) or isinstance(result, float):
            result = self.func['reverse'](result)
        return result, self.arg

    def is_priority(self, dict_vars):
        return self.arg.is_priority(dict_vars)

# COMPOSITES


class AssignNode(TreeNode):
    def __init__(self, var, val):
        self.var, self.val = var, val

    def validate(self, dict_vars):
        self.val.validate(dict_vars)               # don't validate var

    def apply(self, dict_vars=None):
        self.var.assign(self.val.apply(dict_vars), dict_vars)

    def trace(self, level):
        print('.' * level + 'set ')
        self.var.trace(level + 3)
        self.val.trace(level + 3)

#################################################################################
# the parser (syntax analyser, tree builder)
#################################################################################


class Parser:
    def __init__(self, text='', priority='', **kwargs):
        self.lex = Scanner(text)           # make a scanner
        self.vars = kwargs          # add constants
        self.vars['pi'] = 3.14159
        self.vars['_priority'] = priority
        self.func = {
            'sin': Parser.create_func((lambda x: sin(x)), (lambda x: asin(x)), 'asin'),
            'cos': Parser.create_func((lambda x: cos(x)), (lambda x: acos(x)), 'acos'),
            'tan': Parser.create_func((lambda x: tan(x)), (lambda x: atan(x)), 'atan'),
            'arcsin': Parser.create_func((lambda x: asin(x)), (lambda x: sin(x)), 'sin'),
            'arccos': Parser.create_func((lambda x: acos(x)), (lambda x: cos(x)), 'cos'),
            'arctan': Parser.create_func((lambda x: atan(x)), (lambda x: tan(x)), 'tan')
        }
        self.trace_me = TraceDefault
        self.tree = None

    @staticmethod
    def create_func(main, reverse, reverse_name):
        return {
            'main': main,
            'reverse': reverse,
            'reverse_name': reverse_name
        }

    def expression(self, priority):
        self.vars['_priority'] = priority
        variable = deepcopy(self.tree).apply(self.vars)
        result = 0
        while type('') != type(variable):
            result, variable = variable.get_var(result)
        return result

    def parse(self, text):                    # external interface
        if text:
            self.lex.new_text(text)          # reuse with new text
        self.tree = self.analyse()                  # parse string
        # if self.tree:
        #     if self.trace_me:                   # dump parse-tree?
        #         print()
        #         self.tree.trace(0)
        #     if self.errorCheck(self.tree):          # check names
        #         self.interpret(self.tree)           # evaluate tree
        return self

    def analyse(self):
        # try:
        self.lex.scan()                    # get first token
        return self.goal()                 # build a parse-tree
        # except SyntaxError:
        #     print('Syntax Error at column:', self.lex.start)
        #     self.lex.showerror()
        # except LexicalError:
        #     print('Lexical Error at column:', self.lex.start)
        #     self.lex.showerror()

    def error_check(self, tree):
        try:
            tree.validate(self.vars)           # error checker
            return 'ok'
        except UndefinedError as instance:     # args is a tuple
            var_info = instance.args
            print("'%s' is undefined at column: %d" % var_info)
            self.lex.start = var_info[1]
            self.lex.showerror()               # returns None

    def interpret(self, tree):
        result = tree.apply(self.vars)         # tree evals itself
        if result is not None:                     # ignore 'set' result
            print(result)                      # ignores errors

    def goal(self):
        if self.lex.token in ['num', 'var', '(']:
            tree = self.expr()
            self.lex.match('\0')
            return tree
        elif self.lex.token == 'set':
            tree = self.assign()
            self.lex.match('\0')
            return tree
        else:
            raise SyntaxError()

    def assign(self):
        self.lex.match('set')
        var_tree = VarNode(self.lex.value, self.lex.start)
        self.lex.match('var')
        val_tree = self.expr()
        return AssignNode(var_tree, val_tree)               # two subtrees

    def expr(self):
        left = self.factor()                              # left subtree
        while True:
            if self.lex.token in ['\0', ')']:
                return left
            elif self.lex.token == '+':
                self.lex.scan()
                left = PlusNode(left, self.factor())      # add root-node
            elif self.lex.token == '-':
                self.lex.scan()
                left = MinusNode(left, self.factor())     # grows up/right
            else:
                raise SyntaxError()

    def factor(self):
        left = self.factor2()
        while True:
            if self.lex.token in ['+', '-', '\0', ')']:
                return left
            elif self.lex.token == '*':
                self.lex.scan()
                left = TimesNode(left, self.factor2())
            elif self.lex.token == '/':
                self.lex.scan()
                left = DivideNode(left, self.factor2())
            else:
                raise SyntaxError()

    def factor2(self):
        left = self.term()
        while True:
            if self.lex.token in ['+', '-', '\0', ')']:
                return left
            elif self.lex.token == '*':
                return left
            elif self.lex.token == '/':
                return left
            elif self.lex.token == '^':
                self.lex.scan()
                left = PowerNode(left, self.term())
            else:
                raise SyntaxError()

    def term(self):
        if self.lex.token == 'num':
            leaf = NumNode(self.lex.match('num'))
            return leaf
        elif self.lex.token == 'var':
            if self.lex.value in self.func:
                value = self.lex.value
                self.lex.scan()
                arg = self.term()
                leaf = FuncNode(value, self.func[value], arg)
            else:
                leaf = VarNode(self.lex.value, self.lex.start)
                self.lex.scan()
            return leaf
        elif self.lex.token == '(':
            self.lex.scan()
            tree = self.expr()
            self.lex.match(')')
            return tree
        else:
            raise SyntaxError()
