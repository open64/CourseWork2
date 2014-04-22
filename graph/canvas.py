import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler


class GraphCanvas(FigureCanvasTkAgg):
    def __init__(self, figure, parent):
        FigureCanvasTkAgg.__init__(self, figure, parent)
        self.toolbar = NavigationToolbar2TkAgg(self, parent)
        self.toolbar.update()
        self.mpl_connect('key_press_event', self.on_key_event)

    def on_key_event(self, event):
        key_press_handler(event, self, self.toolbar)

