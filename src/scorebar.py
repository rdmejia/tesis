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

class ScoreBar:
    def __init__(self, canvas, left, top, right, bottom, scale):
        self.canvas = canvas
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom
        self.scale = scale

        self.score = 0.0
        self.threshold = 0.0
        self.average = 0.0
        self.points = 0.0

        self.scorebar = ResizableRectangle(
            canvas, 0, 0, 0, 0, fill="red", outline="")
        self.avgbar = ResizableRectangle(
            canvas, 0, 0, 0, 0, fill="dark gray", outline="")
        self.thresholdline = ResizableLine(canvas, 0, 0, 0, 0)

        ResizableRectangle(canvas, left, top, right, bottom)

    def update(self, enabled=True):
        self.points += 1
        if self.points == 1:
            self.average = self.score
        else:
            self.average = self.average * \
                (self.points - 1) / float(self.points) + self.score / float(self.points)

        score = self.score
        threshold = self.threshold
        average = self.average
        if average < 0:
            average = 0
        elif average > self.scale:
            average = self.scale
        if score < 0:
            score = 0
        elif score > self.scale:
            score = self.scale
        if threshold < 0:
            threshold = 0
        elif threshold > self.scale:
            threshold = self.scale

        mid = self.left + (self.right - self.left) * score / self.scale
        avg = self.left + (self.right - self.left) * average / self.scale
        if enabled:
            thresh = self.left + (self.right - self.left) * threshold / self.scale
        else:
            thresh = self.left

        if enabled:
            if mid >= thresh:
                color = "green"
            else:
                color = "red"
        else:
            color = "gray"

        self.scorebar.itemconfig(fill=color)
        self.scorebar.redraw(self.left, self.top, mid, self.bottom)
        self.avgbar.redraw(self.left, self.bottom, avg,
                            self.bottom + (self.bottom - self.top) * 0.25)
        self.thresholdline.redraw(
            thresh, self.top, thresh, self.bottom)