from numpy import *
from matplotlib.figure import Figure
import parser2


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
                arr_result = []
                formula = str(self.result_formula[i]['y']).replace('^', '**')
                for x in self.arr:
                    arr_result.append(eval(formula))
                self.figure.plot(array(arr_result))

    def solution_equations(self, arr_equations, start, finish, step):
        pass