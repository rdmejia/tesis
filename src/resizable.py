import sys
import random
import helptext
from time import sleep
from threading import Timer
from mbientlab.metawear import MetaWear, libmetawear, parse_value
from mbientlab.metawear.cbindings import *
from mbientlab.warble import * 
from resizable import *

if sys.version_info[0] < 3:
    import Tkinter as Tk
    import ttk
else:
    import tkinter as Tk
    from tkinter import ttk, tkMessageBox

class Resizable():
    def __init__(self, canvas):
        self.canvas = canvas
        self.canvas_width_orig = canvas.width
        self.canvas_height_orig = canvas.height

    def redraw(self, x0, y0, x1, y1, **kwargs):
        self.ratio_width = self.canvas.width / float(self.canvas_width_orig)
        self.ratio_height = self.canvas.height / float(self.canvas_height_orig)
        a = x0 * self.ratio_width
        b = y0 * self.ratio_height
        c = x1 * self.ratio_width
        d = y1 * self.ratio_height
        self.canvas.coords(self.object, a, b, c, d, **kwargs)

    def itemconfig(self, **kwargs):
        self.canvas.itemconfig(self.object, **kwargs)


class ResizablePlotPoint(Resizable):
    def __init__(self, canvas, x0, y0, mag, **kwargs):
        Resizable.__init__(self, canvas)
        self.x0 = x0
        self.y0 = y0
        self.mag = mag
        self.size = 3
        self.object = canvas.create_oval(
            x0 - self.size,
            y0 - self.size,
            x0 + self.size,
            y0 + self.size,
            **kwargs)

    def redraw(self, **kwargs):
        self.ratio_width = self.canvas.width / float(self.canvas_width_orig)
        self.ratio_height = self.canvas.height / float(self.canvas_height_orig)
        a = self.x0 * self.ratio_width
        b = self.y0 * self.ratio_height
        self.canvas.coords(
            self.object,
            a - self.size,
            b - self.size,
            a + self.size,
            b + self.size,
            **kwargs)


class ResizableRectangle(Resizable):
    def __init__(self, canvas, x0, y0, x1, y1, **kwargs):
        Resizable.__init__(self, canvas)
        self.object = canvas.create_rectangle(x0, y0, x1, y1, **kwargs)


class ResizableLine(Resizable):
    def __init__(self, canvas, x0, y0, x1, y1, **kwargs):
        Resizable.__init__(self, canvas)
        self.object = canvas.create_line(x0, y0, x1, y1, **kwargs)


class ResizableOval(Resizable):
    def __init__(self, canvas, x0, y0, x1, y1, **kwargs):
        Resizable.__init__(self, canvas)
        self.object = canvas.create_oval(x0, y0, x1, y1, **kwargs)


class ResizableText(Resizable):
    def __init__(self, canvas, x0, y0, **kwargs):
        Resizable.__init__(self, canvas)
        self.object = canvas.create_text(x0, y0, **kwargs)

    def redraw(self, x0, y0, **kwargs):
        self.ratio_width = self.canvas.width / float(self.canvas_width_orig)
        self.ratio_height = self.canvas.height / float(self.canvas_height_orig)
        a = x0 * self.ratio_width
        b = y0 * self.ratio_height
        self.canvas.coords(self.object, a, b, **kwargs)


class ResizableCanvas(Tk.Canvas):
    def __init__(self, parent, **kwargs):
        Tk.Canvas.__init__(self, parent, **kwargs)
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

    def on_resize(self, event):
        # determine the ratio of old width/height to new width/height
        wscale = float(event.width) / self.width
        hscale = float(event.height) / self.height
        self.width = event.width
        self.height = event.height
        # resize the canvas
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        self.scale("all", 0, 0, wscale, hscale)