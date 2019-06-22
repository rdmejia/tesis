VERSION = "1.0.0"

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


class OptionList_Command_MacAddr:

    def __init__(self, parent):
        self.parent = parent

    def set(self, value):  # run when option list is changed
        print "Selected MAC Address " + value
        self.parent.macaddrs.set(value)
        self.parent.macaddr = value
        self.parent.dcb.macaddr_filter = value

class MetaWearState:
    def __init__(self, device):
        self.device = device
        self.samples = 0
        self.callback = FnVoid_VoidP_DataP(self.data_handler)
        self.file = open('metawear.txt', 'w+')
    
    def data_handler(self, ctx, data):
        self.file.write("%s -> %s\n" % (self.device.address, parse_value(data)))
        self.samples+= 1

class GUI:

    def __init__(self, master, dcb):

        # All variables from DigiCue Blue are exposed through class variables
        # in dcb

        self.dcb = dcb
        self.packet_count = dcb.packet_count
        self.master = master
        master.after(500, self.timer)  # register timer
        master.title("CDAG - ASOBIGUA - Version %s" % VERSION)

        self.tabs = ttk.Notebook(master)
        self.tab1 = Tk.Frame(self.tabs, padx=10, pady=10)
        self.tab3 = Tk.Frame(self.tabs, padx=10, pady=10)
        self.tabs.add(self.tab1, text='Tiros')
        self.tabs.add(self.tab3, text='Configurar')
        self.tabs.pack(fill=Tk.BOTH, expand=Tk.YES)

        # Mac addr select
        frame = Tk.Frame(self.tab3)
        frame.pack(fill=Tk.X)
        self.macaddr = None
        self.metawear = None
        self.macaddrs_list = []
        self.macaddr_commands = []
        lbl = Tk.Label(frame, text="Direccion MAC del DigiCue BLue", width=25)
        lbl.pack(side=Tk.LEFT)
        self.macaddrs = Tk.StringVar(frame)
        self.macaddrs.set("<Autodetectar DigiCue>")
        self.macaddrs_combo = Tk.OptionMenu(
            frame, self.macaddrs, "<Autodetectar DigiCue>")
        self.macaddrs_combo.pack(side=Tk.LEFT)

        # MetaWear selection
        frame = Tk.Frame(self.tab3)
        frame.pack(fill=Tk.X)
        label = Tk.Label(frame, text="MetaWear")
        label.pack()

        self.seen_metawears = []
        self.metawear_listbox = Tk.Listbox(frame, selectmode=Tk.MULTIPLE)
        self.metawear_listbox.pack()

        self.btn_connect_metawear = Tk.Button(frame, text="Conectar MetaWears")
        self.btn_connect_metawear.config(command = self.connect_to_metawears_click)
        self.btn_connect_metawear.pack()

        self.options_configig = {}
        fbox = Tk.Frame(self.tab3, relief=Tk.GROOVE, bd=2)
        fbox.pack(fill=Tk.X)

        for label, modes in dcb.config_options:
            frame = Tk.Frame(fbox)
            frame.pack(fill=Tk.X)
            lbl = Tk.Label(frame, text=label, width=25)
            # lbl.pack(side=Tk.LEFT)
            v = Tk.StringVar()
            b = Tk.Radiobutton(
                frame,
                text="Off",
                variable=v,
                value=-1,
                indicatoron=0,
                width=10,
                command=self.check_setting_config)
            # b.pack(side=Tk.LEFT)
            for text, mode in modes:
                if text <> "Off":
                    b = Tk.Radiobutton(
                        frame,
                        text=text,
                        variable=v,
                        value=mode,
                        indicatoron=0,
                        width=10,
                        command=self.check_setting_config)
                    # b.pack(side=Tk.LEFT)
            self.options_configig[label] = v
        
        frame = Tk.Frame(fbox, pady=10)
        frame.pack(fill=Tk.X)
        lbl = Tk.Label(frame, text="", width=25)
        lbl.pack(side=Tk.LEFT)
        self.sync_label = Tk.StringVar(frame)
        self.sync_label.set("Presionar el boton en el DigiCue exactamente una vez para detectar")
        lbl = Tk.Label(frame, textvariable=self.sync_label)
        lbl.pack(side=Tk.LEFT)

        self.mw_devices = []
        self.initialize_metawear()

        # Shots tab
        self.scorebars = ScoreBars(self.tab1, dcb)
        self.btn_start_shot = Tk.Button(self.tab1, text = 'Iniciar tiro')
        self.btn_start_shot.config(command = self.btn_start_shot_click)
        self.btn_start_shot.pack(side = Tk.RIGHT)

    def btn_start_shot_click(self):
        self.mw_states = []
        for device in self.mw_devices:
            # try:
            #     device.connect()
            # except:
            #     print 'connection to %s failed (the device might be already connected)' % device.address
            self.mw_states.append(MetaWearState(device))

        for s in self.mw_states:
            libmetawear.mbl_mw_settings_set_connection_parameters(s.device.board, 7.5, 7.5, 0, 6000)
            sleep(1.5)

            libmetawear.mbl_mw_acc_set_odr(s.device.board, 100.0)
            libmetawear.mbl_mw_acc_set_range(s.device.board, 16.0)
            libmetawear.mbl_mw_acc_write_acceleration_config(s.device.board)

            signal = libmetawear.mbl_mw_acc_get_acceleration_data_signal(s.device.board)
            libmetawear.mbl_mw_datasignal_subscribe(signal, None, s.callback)

            libmetawear.mbl_mw_acc_enable_acceleration_sampling(s.device.board)
            libmetawear.mbl_mw_acc_start(s.device.board)
        
        t = Timer(15, self.time_elapsed)
        t.start()
        print 'shot has started'
        return
    
    def time_elapsed(self):
        print 'shot has finished'
        for s in self.mw_states:
            libmetawear.mbl_mw_acc_stop(s.device.board)
            libmetawear.mbl_mw_acc_disable_acceleration_sampling(s.device.board)

            signal = libmetawear.mbl_mw_acc_get_acceleration_data_signal(s.device.board)
            libmetawear.mbl_mw_datasignal_unsubscribe(signal)
            # libmetawear.mbl_mw_debug_disconnect(s.device.board)
        return

    def handle_metawear_macadresses(self, result):
        if (result.has_service_uuid(MetaWear.GATT_SERVICE) and result.mac not in self.seen_metawears):
            self.metawear_listbox.insert(Tk.END, result.mac)
            self.seen_metawears.append(result.mac)
    
    def initialize_metawear(self):
        BleScanner.set_handler(self.handle_metawear_macadresses)
        BleScanner.start()
    
    def connect_to_metawears_click(self):
        selected = self.metawear_listbox.curselection()
        if (len(selected) == 2):
            self.configure_metawears(selected)
        else:
            tkMessageBox.showinfo("Debe seleccionar al menos 1 metawear")

    def set_led_color(self, mw_mac, led_color):
        device = MetaWear(mw_mac)
        try:
            device.connect()
            self.mw_devices.append(device)
            print "Connected to %s" % mw_mac
        except:
            print "Error connecting to %s" % mw_mac
            return

        pattern = LedPattern(repeat_count= Const.LED_REPEAT_INDEFINITELY)
        libmetawear.mbl_mw_led_load_preset_pattern(byref(pattern), LedPreset.SOLID)
        libmetawear.mbl_mw_led_write_pattern(device.board, byref(pattern), led_color)
        libmetawear.mbl_mw_led_play(device.board)

    def configure_metawears(self, selected):
        mw_mac1 = self.metawear_listbox.get(selected[0])
        self.set_led_color(mw_mac1, LedColor.GREEN)
        mw_mac2 = self.metawear_listbox.get(selected[1])
        self.set_led_color(mw_mac2, LedColor.BLUE)
        return

    def refresh_setting_config(self):
        self.options_configig["Shot Interval"].set(
            self.dcb.threshset_shotpause if self.dcb.setting_shotpause else -1)
        self.options_configig["Backstroke Pause"].set(
            self.dcb.threshset_bspause if self.dcb.setting_bspause else -1)
        self.options_configig["Jab"].set(
            self.dcb.threshset_jab if self.dcb.setting_jab else -1)
        self.options_configig["Follow Through"].set(
            self.dcb.threshset_followthru if self.dcb.setting_followthru else -1)
        self.options_configig["Tip Steer"].set(
            self.dcb.threshset_steering if self.dcb.setting_steering else -1)
        self.options_configig["Straightness"].set(
            self.dcb.threshset_straightness if self.dcb.setting_straightness else -1)
        self.options_configig["Finesse"].set(
            self.dcb.threshset_power if self.dcb.setting_power else -1)
        self.options_configig["Finish"].set(
            self.dcb.threshset_freeze if self.dcb.setting_freeze else -1)
        self.options_configig["Vibrate On Pass"].set(
            self.dcb.setting_vop if self.dcb.setting_vop else -1)
        self.options_configig["Disable All Vibrations"].set(
            self.dcb.setting_dvibe if self.dcb.setting_dvibe else -1)
        self.check_setting_config()

    def check_setting_config(self):

        configuration = {}
        for key in self.options_configig:
            configuration[key] = self.options_configig[key].get()
        self.dcb.set_config(configuration)

        if not self.check_setting_config_test():
            self.sync_label.set("Presione dos veces el boton del DigiCue para sincronizar la configuracion")
        else:
            self.sync_label.set("El DigiCue se encuentra correctamente configurado")

    def check_setting_config_test(self):

        a = 0

        def val(x): return -2 if len(x) == 0 else x

        tmp = int(val(self.options_configig["Shot Interval"].get()))
        if self.dcb.setting_shotpause:
            a += int(tmp == self.dcb.threshset_shotpause)
        else:
            a += int(tmp == -1)

        tmp = int(val(self.options_configig["Backstroke Pause"].get()))
        if self.dcb.setting_bspause:
            a += int(tmp == self.dcb.threshset_bspause)
        else:
            a += int(tmp == -1)

        tmp = int(val(self.options_configig["Jab"].get()))
        if self.dcb.setting_jab:
            a += int(tmp == self.dcb.threshset_jab)
        else:
            a += int(tmp == -1)

        tmp = int(val(self.options_configig["Follow Through"].get()))
        if self.dcb.setting_followthru:
            a += int(tmp == self.dcb.threshset_followthru)
        else:
            a += int(tmp == -1)

        tmp = int(val(self.options_configig["Tip Steer"].get()))
        if self.dcb.setting_steering:
            a += int(tmp == self.dcb.threshset_steering)
        else:
            a += int(tmp == -1)

        tmp = int(val(self.options_configig["Straightness"].get()))
        if self.dcb.setting_straightness:
            a += int(tmp == self.dcb.threshset_straightness)
        else:
            a += int(tmp == -1)

        tmp = int(val(self.options_configig["Finesse"].get()))
        if self.dcb.setting_power:
            a += int(tmp == self.dcb.threshset_power)
        else:
            a += int(tmp == -1)

        tmp = int(val(self.options_configig["Finish"].get()))
        if self.dcb.setting_freeze:
            a += int(tmp == self.dcb.threshset_freeze)
        else:
            a += int(tmp == -1)

        tmp = int(val(self.options_configig["Vibrate On Pass"].get()))
        if self.dcb.setting_vop:
            a += int(tmp == self.dcb.setting_vop)
        else:
            a += int(tmp == -1)

        tmp = int(val(self.options_configig["Disable All Vibrations"].get()))
        if self.dcb.setting_dvibe:
            a += int(tmp == self.dcb.setting_dvibe)
        else:
            a += int(tmp == -1)

        return a == 10

    def refresh_macaddrs(self):
        self.macaddrs.set('')
        self.macaddrs_combo['menu'].delete(0, 'end')
        self.macaddr_commands = []
        for choice in self.macaddrs_list:
            optioncmd = OptionList_Command_MacAddr(self)
            self.macaddr_commands.append(optioncmd)
            command = Tk._setit(optioncmd, choice)
            self.macaddrs_combo['menu'].add_command(
                label=choice, command=command)

    def timer(self):
        if self.dcb.macaddr not in self.macaddrs_list:
            if self.dcb.macaddr <> None:
                # Only add DigiCue Blue devices / correct manuf. ID
                self.macaddrs_list.append(self.dcb.macaddr)
                if self.macaddr is None:
                    self.macaddr = self.dcb.macaddr
                    self.dcb.macaddr_filter = self.macaddr
                self.refresh_macaddrs()
                self.macaddrs.set(self.macaddr)

        if self.packet_count <> self.dcb.packet_count:
            self.packet_count = self.dcb.packet_count

            # Update configuration
            self.refresh_setting_config()

            # Update graphics here
            if self.dcb.data_type == 0:  # Version packet
                pass
            elif self.dcb.data_type == 1:  # update gui if data packet
                self.scorebars.update()

        self.master.after(500, self.timer)
