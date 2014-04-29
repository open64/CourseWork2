from numpy import *
from matplotlib.figure import Figure
import parser2
import parser
import re


class GraphFigures(Figure):
    def __init__(self, start=0.0, end=3.0, step=0.01):
        Figure.__init__(self, figsize=(5, 6), dpi=100)
        self.figure = self.add_subplot(111)
        self.arr = arange(start, end, step)
        self.result_formula = list()

    def _make_equation(self, string):
        try:
            string = string.replace('**', '^')
            left, right = string.split('=')
            right = '+' + right
            for i, symbol in enumerate(right):
                if symbol == '+':
                    right = right[:i] + '-' + right[i+1:]
                elif symbol == '-':
                    right = right[:i] + '+' + right[i+1:]
            string = left + right
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

    def get_result_formula(self, index, unknown):
        result = []
        formula = str(self.result_formula[index][unknown]).replace('^', '**')
        formula = re.sub('[a-zA-Z]+', 'x', formula)
        for x in self.arr:
            result.append(eval(formula))
        return result

    def solution_equations(self, x, y, exactness):
        count = 0
        step = 0.1
        h = 4*step
        arr = [[0, 0], [0, 0]]
        res = [0, 0]

        # while True:
        for i in range(2):
            formula_x = str(self.result_formula[i]['y']).replace('^', '**')
            formula_back_x = re.sub('[a-zA-Z]+', 'back_x', formula_x)
            formula_next_x = re.sub('[a-zA-Z]+', 'next_x', formula_x)

            formula_y = str(self.result_formula[i]['x']).replace('^', '**')
            formula_back_y = re.sub('[a-zA-Z]+', 'back_y', formula_y)
            formula_next_y = re.sub('[a-zA-Z]+', 'next_y', formula_y)
            x_previous = x
            back_x = x - step
            next_x = x + step
            arr[i][0] = (eval(parser.expr(formula_next_x).compile()) - eval(parser.expr(formula_back_x).compile())) / (2*h)

            y_previous = y
            back_y = y - step
            next_y = y + step
            arr[i][1] = (eval(parser.expr(formula_next_y).compile()) - eval(parser.expr(formula_back_y).compile())) / (2*h)
        if arr[0][0] + arr[0][1] < 1 and arr[1][0] + arr[1][1] < 1:
            return x, y
            # if abs(x - x_previous) < exactness and abs(y - y_previous):
            #     break
        count += 1
        return 0, 0