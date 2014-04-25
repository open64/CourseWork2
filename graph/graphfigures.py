from numpy import *
from matplotlib.figure import Figure
import parser2


class GraphFigures(Figure):
    def __init__(self, start=0.0, end=3.0, step=0.01):
        Figure.__init__(self, figsize=(5, 6), dpi=100)
        self.figure = self.add_subplot(111)
        self.arr = arange(start, end, step)
        self.result_formula = None

    def _make_equation(self, string):
        global result
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
            arr_result = []
            parse = parser2.Parser()
            result = parse.parse(string)
            print(result)
            for x in self.arr:
                left = result
                right = ''
                result = 0
                while type('') != type(left):
                    result += left.get_plus()
                    right += str(left.get_plus())
                    left += left.get_plus()
                    if left.times != 1:
                        right = '(' + right + ')/' + str(left.times)
                        result /= left.times
                    if left.power != 1:
                        right = '(' + right + ')^' + str(1 / left.power)
                        result **= 1 / left.power
                    left = left.var
                # print(left, '=', right, sep='')
                # print(result)
                # print()
                arr_result.append(result)
            t = array(arr_result)
        except SyntaxError:
            return None
        except NameError:
            return None
        self.figure.plot(t)
        return result

    def make_figure(self, equation_1, equation_2):
        if equation_1 or equation_2:
            self.result_formula = [self._make_equation(equation_1), self._make_equation(equation_2)]

    def solution_equations(self, arr_equations, start, finish, step):
        pass