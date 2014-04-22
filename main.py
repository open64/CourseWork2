from graph.window import GraphFrame, GraphWindow
import parser2
import re


if __name__ == '__main__':
    x = parser2.Parser(y=10)
    string = '2+4*(3-2*(y+7)**2)-5*3=2-4*4'
    string = string.replace('**', '^')
    left, right = string.split('=')
    right = '+' + right
    for i, char in enumerate(right):
        if char == '+':
            right = right[:i] + '-' + right[i+1:]
        elif char == '-':
            right = right[:i] + '+' + right[i+1:]
    string = left + right
    find_y = re.findall('[-|+].[^y]*y.[^-|+]*', string)
    for y in find_y:


    x.parse(string)
    # GraphFrame(GraphWindow()).mainloop()
