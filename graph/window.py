from tkinter import *
from graph.canvas import GraphCanvas
from graph.graphfigures import GraphFigures


class GraphWindow(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title('???')
        self.geometry('800x600')
        self._make_menu()

    def _make_menu(self):
        self._menu = Menu(self)
        self.config(menu=self._menu)
        file = Menu(self._menu)
        file.add_command(label='New', command=(lambda: None), underline=0)
        file.add_command(label='Open', command=(lambda: None), underline=0)
        file.add_command(label='Save', command=(lambda: None), underline=0)
        self._menu.add_cascade(label='File', menu=file, underline=0)


class GraphFrame(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self._make_widgets()

    def _make_widgets(self):
        self._make_toolbar()
        self._make_panel()
        self._make_graph()

    def _make_toolbar(self):
        pass

    def _make_graph(self):
        self._graph_frame = Frame(self)
        self._graph_frame.pack(side=RIGHT, expand=YES, fill=BOTH)
        self.figure = GraphFigures()
        self._create_graph()

    def _make_panel(self):
        self._panel = Frame(self)
        self._panel.pack(side=LEFT, expand=YES, fill=BOTH)

        Label(self._panel, text='Введіть перше рівняння:').pack(side=TOP, fill=X)
        self._equation_1_entry = Entry(self._panel)
        self._equation_1_entry.insert(0, 'x**2-2*y-y+0.5=0')
        self._equation_1_entry.pack(side=TOP, fill=X)

        Label(self._panel, text='Введіть друге рівняння:').pack(side=TOP, fill=X)
        self._equation_2_entry = Entry(self._panel)
        self._equation_2_entry.insert(0, 'x**2+4*y**2-4=0')
        self._equation_2_entry.pack(side=TOP, fill=X)
        Button(self._panel, text='Створити графік', command=self._create_graph).pack(fill=X)

        Label(self._panel, text='Введіть x:').pack(side=TOP, fill=X, anchor=N)
        self._x_entry = Entry(self._panel)
        self._x_entry.insert(0, str(1.32))
        self._x_entry.pack(side=TOP, fill=X, anchor=N)
        Label(self._panel, text='Введіть y:').pack(side=TOP, fill=X, anchor=N)
        self._y_entry = Entry(self._panel)
        self._y_entry.insert(0, str(0.75))
        self._y_entry.pack(side=TOP, fill=X, anchor=N)
        Label(self._panel, text='Введіть точність:').pack(side=TOP, fill=X, anchor=N)
        self._exactness_entry = Entry(self._panel)
        self._exactness_entry.insert(0, str(0.001))
        self._exactness_entry.pack(side=TOP, fill=X, anchor=N)
        Button(self._panel, text='Розв’язати систему рівнянь', command=self._solution_equations).pack(fill=X)

        self.info_label = Label(self._panel, text='')
        self.info_label.pack(side=BOTTOM, fill=X)

    def _create_graph(self):
        equation1 = self._equation_1_entry.get()
        equation2 = self._equation_2_entry.get()
        self.figure.make_figure(equation1, equation2)

        self._graph = GraphCanvas(self.figure, self._graph_frame)
        self._graph.show()
        self._graph.get_tk_widget().pack(side=TOP, fill=BOTH, expand=0)
        self._graph._tkcanvas.pack(side=TOP, fill=BOTH, expand=0)

    def _solution_equations(self):
        x = float(self._x_entry.get())
        y = float(self._y_entry.get())
        exactness = float(self._exactness_entry.get())
        new_x, new_y = self.figure.solution_equations(x, y, exactness)
        self.info_label.config(text='x = %f; y = %f' % (new_x, new_y))