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

class MetaWearState:
    def __init__(self, device):
        self.device = device
        self.samples = 0
        self.callback = FnVoid_VoidP_DataP(self.data_handler)
        self.file = open('metawear.txt', 'w+')
    
    def data_handler(self, ctx, data):
        self.file.write("%s -> %s\n" % (self.device.address, parse_value(data)))
        self.samples+= 1