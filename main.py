from graph.window import GraphFrame, GraphWindow
import parser2
import re


if __name__ == '__main__':
    x = parser2.Parser()
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
    for r in result:
        left += str(r.get_plus())
    print(left)
    right = 0 - result[0] + result[0].get_plus()
    print(right)
    # print(parser2.Parser().parse('2*(y-5)').apply(1))


    x.parse(string)
    # GraphFrame(GraphWindow()).mainloop()
