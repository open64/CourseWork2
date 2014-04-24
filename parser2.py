"""
Separate expression parsing from evaluation by building an explicit parse tree
"""

TraceDefault = False


class UndefinedError(Exception): pass

if __name__ == '__main__':
    from scanner import Scanner, SyntaxError, LexicalError      # if run here
else:
    from scanner import Scanner, SyntaxError, LexicalError     # from PyTree

#################################################################################
# the interpreter (a smart objects tree)
#################################################################################


class TreeNode:
    def validate(self, dict):           # default error check
        pass

    def apply(self, dict):              # default evaluator
        pass

    def trace(self, level):             # default unparser
        print('.' * level + '<empty>')

# ROOTS


class BinaryNode(TreeNode):
    def __init__(self, left, right):            # inherited methods
        self.left, self.right = left, right     # left/right branches

    def validate(self, dict):
        self.left.validate(dict)                # recurse down branches
        self.right.validate(dict)

    def trace(self, level):
        print('.' * level + '[' + self.label + ']')
        self.left.trace(level+3)
        self.right.trace(level+3)


class PowerNode(BinaryNode):
    label = '^'

    def apply(self, dict):
        return self.left.apply(dict) ** self.right.apply(dict)


class TimesNode(BinaryNode):
    label = '*'

    def apply(self, dict):
        return self.left.apply(dict) * self.right.apply(dict)


class DivideNode(BinaryNode):
    label = '/'

    def apply(self, dict):
        return self.left.apply(dict) / self.right.apply(dict)


class PlusNode(BinaryNode):
    label = '+'

    def apply(self, dict):
        return self.left.apply(dict) + self.right.apply(dict)


class MinusNode(BinaryNode):
    label = '-'

    def apply(self, dict):
        return self.left.apply(dict) - self.right.apply(dict)

# LEAVES


class NumNode(TreeNode):
    def __init__(self, num):
        self.num = num                 # already numeric

    def apply(self, dict):             # use default validate
        return self.num

    def trace(self, level):
        print('.' * level + repr(self.num))   # as code, was 'self.num'


class VarNode(TreeNode):
    def __init__(self, text, start, times=1, plus=0, power=1):
        self.name = text                    # variable name
        self.var = text
        self.power = power
        self.times = times
        self.plus = plus
        self.column = start                   # column for errors

    def __mul__(self, other):
        self.times *= other
        self.plus *= other
        return self

    def __rmul__(self, other):
        self.times *= other
        self.plus *= other
        return self

    def __add__(self, other):
        self.plus += other
        return self

    def __radd__(self, other):
        self.plus += other
        return self

    def __sub__(self, other):
        self.plus -= other
        return self

    def __rsub__(self, other):
        self.times = -self.times
        self.plus = other - self.plus
        return self

    def __div__(self, other):
        self.times /= other
        return self

    def __pow__(self, power, modulo=None):
        self.times **= power
        self.power *= power
        self.plus = VarNode(self.var, None, self.plus*2, self.plus**power)
        return self

    def __gt__(self, other):
        return self.times > other

    def __lt__(self, other):
        return self.times < other

    def __rpow__(self, power, modulo=None):
        self.times **= power
        self.power **= power
        self.plus = VarNode(self.var, None, self.plus*2, self.plus**power)
        return self

    def validate(self, dict):
        if not self.name in dict.keys():
            raise UndefinedError(self.name, self.column)

    def apply(self, dict):
        return self                # validate before apply

    def assign(self, value, dict):
        dict[self.name] = value               # local extension

    def trace(self, level):
        print('.' * level + self.name)

    def __str__(self):
        string = ''
        if self.times != 1:
            string += str(self.times) + '*'
        string += str(self.var)
        if self.power != 1:
            string += '^' + str(self.power)
        if self.plus > 0:
            string += '+' + str(self.plus)
        elif self.plus < 0:
            string += str(self.plus)
        return string

# COMPOSITES


class AssignNode(TreeNode):
    def __init__(self, var, val):
        self.var, self.val = var, val

    def validate(self, dict):
        self.val.validate(dict)               # don't validate var

    def apply(self, dict):
        self.var.assign( self.val.apply(dict), dict )

    def trace(self, level):
        print('.' * level + 'set ')
        self.var.trace(level + 3)
        self.val.trace(level + 3)

#################################################################################
# the parser (syntax analyser, tree builder)
#################################################################################


class Parser:
    def __init__(self, text='', **kwargs):
        self.lex = Scanner(text)           # make a scanner
        self.vars = kwargs          # add constants
        self.vars['pi'] = 3.14159
        self.traceme = TraceDefault

    def parse(self, *text):                    # external interface
        if text:
            self.lex.new_text(text[0])          # reuse with new text
        tree = self.analyse()                  # parse string
        if tree:
            if self.traceme:                   # dump parse-tree?
                print()
                tree.trace(0)
            # if self.errorCheck(tree):          # check names
            #     self.interpret(tree)           # evaluate tree
        return tree

    def analyse(self):
        try:
            self.lex.scan()                    # get first token
            return self.Goal()                 # build a parse-tree
        except SyntaxError:
            print('Syntax Error at column:', self.lex.start)
            self.lex.showerror()
        except LexicalError:
            print('Lexical Error at column:', self.lex.start)
            self.lex.showerror()

    def errorCheck(self, tree):
        try:
            tree.validate(self.vars)           # error checker
            return 'ok'
        except UndefinedError as instance:     # args is a tuple
            varinfo = instance.args
            print("'%s' is undefined at column: %d" % varinfo)
            self.lex.start = varinfo[1]
            self.lex.showerror()               # returns None

    def interpret(self, tree):
        result = tree.apply(self.vars)         # tree evals itself
        if result is not None:                     # ignore 'set' result
            print(result)                      # ignores errors

    def Goal(self):
        if self.lex.token in ['num', 'var', '(']:
            tree = self.Expr()
            self.lex.match('\0')
            return tree
        elif self.lex.token == 'set':
            tree = self.Assign()
            self.lex.match('\0')
            return tree
        else:
            raise SyntaxError()

    def Assign(self):
        self.lex.match('set')
        vartree = VarNode(self.lex.value, self.lex.start)
        self.lex.match('var')
        valtree = self.Expr()
        return AssignNode(vartree, valtree)               # two subtrees

    def Expr(self):
        left = self.Factor()                              # left subtree
        while True:
            if self.lex.token in ['\0', ')']:
                return left
            elif self.lex.token == '+':
                self.lex.scan()
                left = PlusNode(left, self.Factor())      # add root-node
            elif self.lex.token == '-':
                self.lex.scan()
                left = MinusNode(left, self.Factor())     # grows up/right
            else:
                raise SyntaxError()

    def Factor(self):
        left = self.Term()
        while True:
            if self.lex.token in ['+', '-', '\0', ')']:
                return left
            elif self.lex.token == '*':
                self.lex.scan()
                left = TimesNode(left, self.Factor2())
            elif self.lex.token == '/':
                self.lex.scan()
                left = DivideNode(left, self.Factor2())
            else:
                raise SyntaxError()

    def Factor2(self):
        left = self.Term()
        while True:
            if self.lex.token in ['+', '-', '\0', ')']:
                return left
            elif self.lex.token == '*':
                return left
            elif self.lex.token == '/':
                return left
            elif self.lex.token == '^':
                self.lex.scan()
                left = PowerNode(left, self.Term())
            else:
                raise SyntaxError()


    def Term(self):
        if self.lex.token == 'num':
            leaf = NumNode(self.lex.match('num'))
            return leaf
        elif self.lex.token == 'var':
            leaf = VarNode(self.lex.value, self.lex.start)
            self.lex.scan()
            return leaf
        elif self.lex.token == '(':
            self.lex.scan()
            tree = self.Expr()
            self.lex.match(')')
            return tree
        else:
            raise SyntaxError()

#################################################################################
# self-test code: use my parser, parser1's tester
#################################################################################

if __name__ == '__main__':
    import testparser
    testparser.test(Parser, 'parser2')    #  run with Parser class here