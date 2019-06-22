import sys
import random
import helptext
from time import sleep
from threading import Timer
from mbientlab.metawear import MetaWear, libmetawear, parse_value
from mbientlab.metawear.cbindings import *
from mbientlab.warble import * 
from resizable import *
from scorebar import *

if sys.version_info[0] < 3:
    import Tkinter as Tk
    import ttk
else:
    import tkinter as Tk
    from tkinter import ttk, tkMessageBox

class Plot:

    def __init__(self, canvas, left, top, size):
        self.canvas = canvas
        self.canvas_width_orig = canvas.width
        self.canvas_height_orig = canvas.height
        self.left = left
        self.top = top
        self.size = size
        self.points = []

        ResizableRectangle(
            self.canvas,
            self.left,
            self.top,
            self.left +
            self.size,
            self.top +
            self.size)
        ResizableLine(
            self.canvas,
            self.left,
            self.top + self.size / 2,
            self.left + self.size,
            self.top + self.size / 2)
        ResizableLine(
            self.canvas,
            self.left + self.size / 2,
            self.top,
            self.left + self.size / 2,
            self.top + self.size)

        # Make circles at 35,20,10,5 (thresholds for straightness)
        x0 = self.left + self.size / 2
        y0 = self.top + self.size / 2
        self.x0 = x0
        self.y0 = y0
        r = 0.5
        self.threshold_circle = ResizableOval(
            self.canvas, x0 - r, y0 - r, x0 + r, y0 + r)

    def plot(self, x, y, **kwargs):
        # Plots point in plot area. Limits are -1 to 1
        if x > 1:
            x = 1.
        if y > 1:
            y = 1.
        if x < -1:
            x = -1.
        if y < -1:
            y = -1.
        mag = (x**2 + y**2)**0.5
        x = (x * self.size / 2 + self.x0) * self.canvas.width / (float(self.canvas_width_orig))
        y = (y * self.size / 2 + self.y0) * self.canvas.height / (float(self.canvas_height_orig))
        self.points.append(
            ResizablePlotPoint(
                self.canvas, x, y, mag, **kwargs))

    def update(self, threshold):
        self.threshold = threshold
        r = threshold * self.size / 2
        self.threshold_circle.redraw(
            self.x0 - r, self.y0 - r, self.x0 + r, self.y0 + r)
        for i in xrange(0, len(self.points)):
            point = self.points[i]
            if i == (len(self.points) - 1):
                if point.mag > self.threshold:
                    color = "red"
                else:
                    color = "green"
            else:
                color = "dark gray"
            point.itemconfig(fill=color)
            point.redraw()  