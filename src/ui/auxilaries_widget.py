"""
Module containing some custom QtWidgets.

This module contains several custom widgets that are integrated with PyQt/PySide, matplotlib,
and a logging system for building a GUI that supports visualization and real-time log display.

Classes
-------
MplCanvas : FigureCanvasQTAgg
    A matplotlib canvas for rendering plots within PyQt/PySide applications.
PlotWidget : QWidget
    A QWidget that embeds a matplotlib canvas and navigation toolbar.
MultiPlotWidget : PlotWidget
    A QWidget that supports multiple plots with a dropdown picker to select between them.
MyLogHandler : logging.Handler
    A custom log handler that outputs log messages to a QPlainTextEdit widget.
WebPlotWidget : QWidget
    A QWidget that displays HTML-based graphs using a web engine.
QPlainTextEditLogger : QPlainTextEdit
    A QPlainTextEdit widget that serves as a logging display with a custom handler.
"""

from PySide6.QtWidgets import (
    QWidget, 
    QFileDialog, 
    QVBoxLayout,
    QHBoxLayout,
    QPlainTextEdit,
    QPushButton, 
    QComboBox
)
from PySide6 import QtCore, QtWidgets, QtWebEngineWidgets
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg, 
    NavigationToolbar2QT as NavigationToolbar
)
from logging import(
    Handler, 
    Formatter
)

from ui.VTKWindow import VtkViewer


class MplCanvas(FigureCanvasQTAgg):
    """A matplotlib canvas widget that can be embedded in a PyQt/PySide application.
    
    This class wraps a matplotlib `FigureCanvasQTAgg` and provides methods 
    for plotting figures and axes.

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget.
    width : float, optional
        Width of the canvas (default is 5).
    height : float, optional
        Height of the canvas (default is 4).
    dpi : int, optional
        Dots per inch for the canvas (default is 100).
    """
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super(MplCanvas, self).__init__(self.fig)

    def plot_ax(self, plot_func):
        """Clears the current axis and applies the provided plot function.

        Parameters
        ----------
        plot_func : callable
            A function that takes an axis (`ax`) as a parameter and applies plotting.
        """
        self.fig.clf()
        ax = self.fig.add_subplot()
        plot_func(ax)
        self.draw()

    def plot_fig(self, plot_func):
        """Clears the current figure and applies the provided plot function.

        Parameters
        ----------
        plot_func : callable
            A function that takes a `Figure` object as a parameter and applies plotting.
        """
        self.fig.clf()
        plot_func(self.fig)
        self.draw()




class PlotWidget(QWidget):
    """A QWidget containing a matplotlib canvas and navigation toolbar.
    
    This widget is designed to allow plotting using matplotlib within a PyQt/PySide application.
    """
    def __init__(self):
        """Initializes the plot widget by creating a canvas and a navigation toolbar.
        """
        super(PlotWidget, self).__init__()
        self.canvas = MplCanvas()
        toolbar = NavigationToolbar(self.canvas, self)
        
        self.layout = QVBoxLayout()
        self.layout.addWidget(toolbar)
        self.layout.addWidget(self.canvas)

        self.setLayout(self.layout)
        ##
        # vlayout = QtWidgets.QVBoxLayout(self)
        
        # vlayout.addWidget(self.browser)
        # print(vlayout)

    def plot_ax(self, plot_func):
        """Plots on the current axis using the provided plot function.

        Parameters
        ----------
        plot_func : callable
            A function that takes an axis (`ax`) as input and applies plotting.
        """
        self.canvas.plot_ax(plot_func)
    
    def plot_fig_3dmodel(self, plot_func):
        self.canvas.plot_fig(plot_func)

    def plot_fig(self, plot_func):
        """Plots on the current figure using the provided plot function.

        Parameters
        ----------
        plot_func : callable
            A function that takes a `Figure` object as input and applies plotting.
        """
        self.canvas.plot_fig(plot_func)

    def clear(self):
        """Clears the plot by applying an empty function to the canvas.
        """
        self.canvas.plot_fig(lambda *arg: None)

class MultiPlotWidget(PlotWidget):
    """A QWidget that supports multiple plots with a dropdown picker to select between them.
    Inherits from `PlotWidget`.
    """
    def __init__(self):
        """Initializes the multi-plot widget with a dropdown picker.
        """
        super().__init__()
        self.picker = QComboBox(self)
        self.layout.addWidget(self.picker)
        self.setLayout(self.layout)
        self.plot_func = lambda *args: None
        self.picker.currentIndexChanged.connect(self.plot_fig_on_picker)
    
    def update_plot(self, items, plot_func):
        """Updates the plot with a new set of items and a plot function.

        Parameters
        ----------
        items : list of str
            The items to populate the dropdown picker with.
        plot_func : callable
            A function that takes the selected index and a `Figure` object as input and plot the layer with that index.
        """
        self.plot_fig(lambda *arg: None) #Clear the figure if update
        self.picker.currentIndexChanged.disconnect() #Disconnect plot function
        
        self.picker.clear()
        self.picker.addItems(items) #Clear then add items
        
        self.plot_func = plot_func 
        self.plot_fig_on_picker() #Replot
        self.picker.currentIndexChanged.connect(self.plot_fig_on_picker) #Replot if change index

    def plot_fig_on_picker(self):
        """Re-plots the figure based on the currently selected index in the picker.
        """
        i = self.picker.currentIndex()
        f = lambda fig: self.plot_func(i, fig)
        self.plot_fig(f)

class WebPlotWidget(QWidget):
    """A QWidget for displaying HTML-based graphs (Plotly or Fullcontrol) or visualizations using a web engine.
    """
    def __init__(self, parent=None):
        """Initializes the web plot widget with a QWebEngineView for displaying HTML content.
        
        Parameters
        ----------
        parent : QWidget, optional
            The parent widget (default is None).
        """
        super().__init__(parent)
        self.browser = QtWebEngineWidgets.QWebEngineView(self)

        vlayout = QtWidgets.QVBoxLayout(self)
        vlayout.addWidget(self.browser)

    def show_graph(self, html):
        """Displays a graph using the provided HTML content.
        
        Parameters
        ----------
        html : str
            HTML content representing the graph to be displayed.
        """
        self.browser.setHtml(html)

    def clear(self):
        """Clears the graph display.
        """
        self.browser.setHtml('')

class WebPlotWidget1(QWidget):
    """A QWidget for displaying HTML-based graphs (Plotly or Fullcontrol) or visualizations using a web engine.
    """
    def __init__(self, parent=None):
        """Initializes the web plot widget with a QWebEngineView for displaying HTML content.
        
        Parameters
        ----------
        parent : QWidget, optional
            The parent widget (default is None).
        """
        super().__init__(parent)
        # self.browser = QtWebEngineWidgets.QWebEngineView(self)
        
        # vlayout = QtWidgets.QVBoxLayout(self)
        self.browser = VtkViewer(self)
        vlayout = QtWidgets.QVBoxLayout(self)
        vlayout.addWidget(self.browser)
        print(vlayout)

    def plot_fig_3dmodel(self, plot_func):
        print("IM BEING PLOT HERE")
        # self.canvas.plot_fig(plot_func)

    def show_graph(self, html):
        """Displays a graph using the provided HTML content.
        
        Parameters
        ----------
        html : str
            HTML content representing the graph to be displayed.
        """
        self.browser.setHtml(html)

    def clear(self):
        """Clears the graph display.
        """
        self.browser.setHtml('')

class MyLogHandler(Handler):
    """A custom logging handler that outputs log messages to a QPlainTextEdit widget.
    
    Parameters
    ----------
    textedit : QPlainTextEdit
        The text edit widget where log messages will be displayed.
    """
    def __init__(self, textedit):
        super().__init__()
        self.textedit = textedit

    def emit(self, record):
        """Formats and appends the log record to the associated QPlainTextEdit widget.

        Parameters
        ----------
        record : LogRecord
            The log record that contains the log message.
        """
        msg = self.format(record)
        self.textedit.appendPlainText(msg)

class QPlainTextEditLogger(QPlainTextEdit):
    """ A QPlainTextEdit widget that serves as a logging display with a custom handler.
    """
    def __init__(self, parent=None):
        """ Initializes the text edit logger and attaches a custom log handler.
        
        Parameters
        ----------
        parent : QWidget, optional
            The parent widget (default is None).
        """
        super().__init__(parent)
        self.setReadOnly(True)
        self.handler = MyLogHandler(self) #Attach custom log handler
    
    def getHandler(self):
        self.handler.setFormatter(Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        return self.handler