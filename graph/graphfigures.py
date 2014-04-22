from numpy import *
from debian.deb822 import _CaseInsensitiveString
from matplotlib.figure import Figure
import parser


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
            string.replace('**', '^')
            func = parser.expr(string)
            func = func.compile()
            t = array([eval(func) for x in arr])
        except SyntaxError:
            return None
        except NameError:
            return None
        figure.plot(t)
