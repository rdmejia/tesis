#!/usr/bin/env python

# Nathan Rhoades 10/13/2017

import serial
import serialport
import bgapi
import gui
import digicueblue
import traceback
import time
import threading
import sys
from mbientlab.metawear import libmetawear
from login import *

if sys.version_info[0] < 3:
    import Tkinter as Tk
else:
    import tkinter as Tk


class App(threading.Thread):  # thread GUI to that BGAPI can run in background

    def __init__(self, dcb, trainer, player):
        self.dcb = dcb
        self.trainer = trainer
        self.player = player
        threading.Thread.__init__(self)
        self.start()

    def callback(self):
        self.root.quit()

    def closed_window(self):
        for device in self.gui.mw_devices:
            try:
                libmetawear.mbl_mw_led_stop_and_clear(device.board)
                device.disconnect()
            except:
                print "disconnection might have failed"
        self.root.destroy()

    def run(self):
        try:
            self.root = Tk.Tk()
            self.gui = gui.GUI(self.root, self.dcb, self.trainer, self.player)
            self.root.protocol('WM_DELETE_WINDOW', self.closed_window)
            self.root.mainloop()
        except BaseException:
            pass
        finally:
            self.closed_window()


def main():
    login = Login()

    if login.trainer == None or login.player == None:
        exit()

    try:
        f = open("comport.cfg", "r")
        comport = f.readline().strip(' ')
        f.close()
    except BaseException:
        # open comport selection gui
        serialport.launch_selection()
        return
    try:
        # open serial port and launch application
        print "Opening %s" % comport
        ser = serial.Serial(comport, 115200, timeout=1, writeTimeout=1)
        dcb = digicueblue.DigicueBlue(filename="data.csv", debugprint=False)
        app = App(dcb, login.trainer, login.player)
        bg = bgapi.Bluegiga(dcb, ser, debugprint=True)
    except BaseException:
        print traceback.format_exc()
        try:
            ser.close()
        except BaseException:
            pass
        text = """Please make sure the BLED112 dongle is plugged into the COM port
                specified in comport.cfg, and that no other programs are using the port.
                Use the serialport GUI to help select the correct port."""
        text = text.replace('\n', ' ')
        text = text.replace('\t', '')
        print text
        serialport.launch_selection()


if __name__ == '__main__':
    main()
