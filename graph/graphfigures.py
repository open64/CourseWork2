from numpy import arange, array
from matplotlib.figure import Figure
from math import asin, sin, cos, acos, tan, atan
import parser2
import parser
# import re


class GraphFigures(Figure):
    def __init__(self, start=0.0, end=3.0, step=0.01):
        Figure.__init__(self, figsize=(5, 6), dpi=100)
        self.figure = self.add_subplot(111)
        self.arr = arange(start, end, step)
        self.result_formula = list()
        self.formula = list()

    def _make_equation(self, string):
        try:
            left, right = string.split('=')
            right = '+' + right
            for i, symbol in enumerate(right):
                if symbol == '+':
                    right = right[:i] + '-' + right[i+1:]
                elif symbol == '-':
                    right = right[:i] + '+' + right[i+1:]
            string = left + (right if eval(right) else '')
            self.formula.append(string)
            string = string.replace('**', '^')
            parse = parser2.Parser().parse(string)
            self.result_formula.append(dict())
            for variable in ['x', 'y']:
                self.result_formula[-1][variable] = parse.expression(variable)
        except SyntaxError:
            return None
        except NameError:
            return None

    def make_figure(self, equation_1, equation_2):
        if equation_1 and equation_2:
            for i, equation in enumerate([equation_1, equation_2]):
                self._make_equation(equation)
                self.figure.plot(array(self.get_result_formula(i, 'y')))

    def get_result_formula(self, index, unknown, start=0, end=3.0, step=0.001):
        result = []
        formula = str(self.result_formula[index][unknown]).replace('^', '**')
        # formula = re.sub('[a-zA-Z]+', 'x', formula)
        if start:
            self.arr = arange(start, end, step)
        for x in self.arr:
            try:
                result.append(eval(parser.expr(formula).compile()))
            except ValueError:
                continue
        return result

    def get_result(self, index, x, y):
        return eval(parser.expr(self.formula[index]).compile())

    def rotate_matrix(self, a):
        det = a[0][0]*a[1][1] - a[0][1]*a[1][0]
        if det:
            aa = a[0][0]
            a[0][0] = a[1][1]/det
            a[1][1] = aa/det
            a[0][1] = -a[0][1]/det
            a[1][0] = -a[1][0]/det
            return a

    def solution_equations(self, x, y, exactness):
        h = exactness
        arr = [[0 for i in range(2)] for j in range(2)]
        res = 2*exactness
        while res >= exactness:
            arr[0][0] = (self.get_result(0, x+exactness, y) - self.get_result(0, x-exactness, y)) / (2*h)
            arr[0][1] = (self.get_result(0, x, y+exactness) - self.get_result(0, x, y-exactness)) / (2*h)
            arr[1][0] = (self.get_result(1, x+exactness, y) - self.get_result(1, x-exactness, y)) / (2*h)
            arr[1][1] = (self.get_result(1, x, y+exactness) - self.get_result(1, x, y-exactness)) / (2*h)
            arr = self.rotate_matrix(arr)
            if arr:
                dx = -arr[0][0]*self.get_result(0, x, y) + -arr[0][1]*self.get_result(1, x, y)
                dy = -arr[1][0]*self.get_result(0, x, y) + -arr[1][1]*self.get_result(1, x, y)
                x += dx
                y += dy
                res1 = self.get_result(0, x, y)
                res2 = self.get_result(1, x, y)
                res = (res1**2 + res2**2)**0.5
            else:
                arr = [[0 for i in range(2)] for j in range(2)]
        return x, y