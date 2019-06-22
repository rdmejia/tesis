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
from plot import *
from scorebarshandler import *

if sys.version_info[0] < 3:
    import Tkinter as Tk
    import ttk
else:
    import tkinter as Tk
    from tkinter import ttk, tkMessageBox

class ScoreBars:

    def __init__(self, frame, dcb):

        self.dcb = dcb
        self.frame = frame

        self.canvas = ResizableCanvas(
            self.frame,
            width=810,
            height=400,
            highlightthickness=0)
        self.canvas.pack(fill=Tk.BOTH, expand=Tk.YES)

        left = 300
        right = 550
        self.bars = []
        self.scores = []
        self.labels = (
            'Finalizacion',
            'Sutileza',
            'Rectitud',
            'Direccion de la punta',
            'Seguimiento del taco',
            'Golpe',
            'Pausa atras',
            'Intervalo de tiro')
        self.scale = (3.0, 10.0, 10.0, 10.0, 10.0, 10.0, 1.0, 60.0)
        self.score_format = (
            "%0.2fs",
            "%0.1f",
            "%0.1f",
            "%0.1f",
            "%0.1f",
            "%0.1f",
            "%0.2fs",
            "%0.1fs")
        self.outof = ('/3s', '/10', '/10', '/10', '/10', '/10', '/1s', '/60s')
        for i in xrange(0, 8):
            top = i * 400 / 8. + 10
            bottom = (i + 1) * 400 / 8. - 10
            self.bars.append(
                ScoreBar(
                    self.canvas,
                    left,
                    top,
                    right,
                    bottom,
                    self.scale[i]))
            ResizableRectangle(self.canvas, 10, top, left - 10, bottom)
            ResizableRectangle(self.canvas, left - 10, top, left - 100, bottom)
            ResizableText(self.canvas, 100, top + (bottom - top)
                          * 0.5, text=self.labels[i], font=("Purisa", 14))
            ResizableText(self.canvas, 575, top + (bottom - top)
                          * 0.5, text=self.outof[i], font=("Purisa", 14))
            self.scores.append(ResizableText(
                self.canvas, left - 55, top + (bottom - top) * 0.5, text="0", font=("Purisa", 18)))

        # Plot area
        self.plot = Plot(self.canvas, 600, 100, 200)
        ResizableText(
            self.canvas,
            700,
            75,
            text="Rectitud",
            font=(
                "Purisa",
                14))

    def _update_scores(self):
        for i in xrange(0, 8):
            text = self.score_format[i] % self.bars[i].score
            self.scores[i].itemconfig(text=text)

    def test(self):

        for bar in self.bars:
            bar.average = bar.scale * random.random()
            bar.score = bar.scale * random.random()
            bar.threshold = bar.scale * random.random()
            bar.update(True)
        self._update_scores()
        x = random.normalvariate(0, 0.5)
        y = random.normalvariate(0, 0.5)
        self.plot.plot(x, y)
        self.plot.update(random.random())

    def update(self):
        dcb = self.dcb

        self.bars[0].score = dcb.score_freeze
        self.bars[0].threshold = dcb.threshold_freeze
        self.bars[0].update(dcb.setting_freeze)

        self.bars[1].score = dcb.score_power
        self.bars[1].threshold = dcb.threshold_power
        self.bars[1].update(dcb.setting_power)

        self.bars[2].score = dcb.score_straightness
        self.bars[2].threshold = dcb.threshold_straightness
        self.bars[2].update(dcb.setting_straightness)

        self.bars[3].score = dcb.score_steering
        self.bars[3].threshold = dcb.threshold_steering
        self.bars[3].update(dcb.setting_steering)

        self.bars[4].score = dcb.score_followthru
        self.bars[4].threshold = dcb.threshold_followthru
        self.bars[4].update(dcb.setting_followthru)

        self.bars[5].score = dcb.score_jab
        self.bars[5].threshold = dcb.threshold_jab
        self.bars[5].update(dcb.setting_jab)

        self.bars[6].score = dcb.score_bspause
        self.bars[6].threshold = dcb.threshold_bspause
        self.bars[6].update(dcb.setting_bspause)

        self.bars[7].score = dcb.score_shotpause
        self.bars[7].threshold = dcb.threshold_shotpause
        self.bars[7].update(dcb.setting_shotpause)

        self._update_scores()

        x = dcb.impactx / 50.
        y = dcb.impacty / 50.
        thresh = (50 - 5 * dcb.threshold_straightness) / 50.
        self.plot.plot(x, y)
        self.plot.update(thresh)