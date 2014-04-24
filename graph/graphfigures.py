from _ast import arg
from numpy import *
from matplotlib.figure import Figure
import parser2
import re


class GraphFigures(Figure):
    def __init__(self):
        Figure.__init__(self, figsize=(5, 6), dpi=100)

    def make_figure(self, equation_1, equation_2, start=0.0, end=3.0, step=0.01):
        if equation_1 or equation_2:
            figure = self.add_subplot(111)
            arr = arange(start, end, step)
            self._make_equation(figure, equation_1, arr)
            self._make_equation(figure, equation_2, arr)

    def _make_equation(self, figure, string, arr):
        try:
            string = string.replace('**', '^')
            left, right = string.split('=')
            right = '+' + right
            for i, char in enumerate(right):
                if char == '+':
                    right = right[:i] + '-' + right[i+1:]
                elif char == '-':
                    right = right[:i] + '+' + right[i+1:]
            string = left + right
            arr_result = []
            for x in arr:
                parse = parser2.Parser(x=x)
                result = parse.parse(string)
                left = result
                right = ''
                result = 0
                while type(left) != type(''):
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
                print(left, '=', right, sep='')
                print(result)
                print()
                arr_result.append(result)
            # func = parser.expr(string)
            # func = func.compile()
            t = array(arr_result)
        except SyntaxError:
            return None
        except NameError:
            return None
        figure.plot(t)

    def parse(self):
        string = '2+4*(3-2*(y+7)**2)-5*3=2-4*4'
        string = string.replace('**', '^')
        find_y = re.findall('[-|+].[^y]*y.[^-|+]*', string)
        result = [parser2.Parser().parse(y[1:]).apply() for y in find_y]
        for i in result:
            print(i.apply(1))
        left = ''
        prev_pos = 0
        next_pos = 0
        for s in find_y:
            next_pos = string.find(s)
            left += string[prev_pos:next_pos]
            prev_pos = next_pos + len(s)
        left += string[prev_pos:]
        print(right)
        right = result[0]
        print()
        right = 0 - right
        while type(right) != type(''):
            # for r in result:
            #     left += str(r.get_plus())
            left += str(right.get_plus())
            right = right + result[0].get_plus()
            left = '(' + '(' + left + ')/' + str(right.times) + ')^' + str(1 / right.power)
            right = right.var
            string = left + '=' + str(right)
        print(string)
