VERSION = "1.0.0"

import sys
import random
import helptext
import datetime
import requests
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

API_BASE_URL = "https://mocktesisasobiguaapi.azurewebsites.net/v1"
# API_BASE_URL = "https://localhost:5001/v1"
HEADER = {"Content-Type": "application/json", "Accept": "*"}

class OptionList_Command_MacAddr:

    def __init__(self, parent):
        self.parent = parent

    def set(self, value):  # run when option list is changed
        print "Selected MAC Address " + value
        self.parent.macaddrs.set(value)
        self.parent.macaddr = value
        self.parent.dcb.macaddr_filter = value

class MetaWearState:
    def __init__(self, device, position, gui):
        self.device = device
        self.samples = 0
        self.callback = FnVoid_VoidP_DataP(self.data_handler)
        self.position = position
        self.gui = gui
        self.file = open('metawear.txt', 'w+')
    
    def data_handler(self, ctx, data):
        parsed = parse_value(data)
        # self.file.write("%s -> %s\n" % (self.device.address, parsed))
        xyz_shot = {
            "timeStamp": datetime.datetime.utcnow().isoformat(),
            "x": parsed.x,
            "y": parsed.y,
            "z": parsed.z,
            "xyzShotPosition": self.position
        }
        self.gui.xyz_shots.append(xyz_shot)
        # self.samples+= 1

class GUI:

    def __init__(self, master, dcb, trainer, player):

        # All variables from DigiCue Blue are exposed through class variables
        # in dcb

        self.dcb = dcb
        self.trainer = trainer
        self.player = player
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
        self.mw_positions = {}
        self.xyz_shots = []
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
        self.btn_start_shot = Tk.Button(self.tab1, text = 'Iniciar tiro', bg='green', width=75, height=3)
        self.btn_start_shot.config(command = self.btn_start_shot_click)
        self.btn_start_shot.pack(side = Tk.BOTTOM)

    def btn_start_shot_click(self):
        self.mw_states = []
        self.xyz_shots = []
        for device in self.mw_devices:
            # try:
            #     device.connect()
            # except:
            #     print 'connection to %s failed (the device might be already connected)' % device.address
            self.mw_states.append(MetaWearState(device, self.mw_positions[device.address], self))

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
        
        # t = Timer(15, self.time_elapsed)
        # t.start()
        print 'shot has started'
        return
    
    def time_elapsed(self):
        print 'shot has finished'
        self.stop_metawears()
        return

    def stop_metawears(self):
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
        if (len(selected) == 3):
            self.configure_metawears(selected)
        else:
            tkMessageBox.showinfo("Debe seleccionar 3 metawears")

    def set_led_color(self, mw_mac, led_color, position):
        device = MetaWear(mw_mac)
        i = 0
        connected = False
        while i < 3 and not connected:
            try:
                device.connect()
                connected = True
                self.mw_devices.append(device)
                self.mw_positions[mw_mac] = position
                print "Connected to %s" % mw_mac
            except:
                i = i + 1
                print "Connection to %s failed. Retrying..." % mw_mac
            
            if not connected:
                print "Error connecting to %s" % mw_mac
                return

        pattern = LedPattern(repeat_count= Const.LED_REPEAT_INDEFINITELY)
        libmetawear.mbl_mw_led_load_preset_pattern(byref(pattern), LedPreset.SOLID)
        libmetawear.mbl_mw_led_write_pattern(device.board, byref(pattern), led_color)
        libmetawear.mbl_mw_led_play(device.board)

    def configure_metawears(self, selected):
        mw_mac1 = self.metawear_listbox.get(selected[0])
        self.set_led_color(mw_mac1, LedColor.GREEN, "Antebrazo")
        mw_mac2 = self.metawear_listbox.get(selected[1])
        self.set_led_color(mw_mac2, LedColor.BLUE, "Muneca")
        mw_mac3 = self.metawear_listbox.get(selected[2])
        self.set_led_color(mw_mac3, LedColor.RED, "Pierna")
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
                self.stop_metawears()
                self.persist_shot()

        self.master.after(500, self.timer)
    
    def persist_shot(self):
        payload = str({
            "backstrokePause": self.dcb.score_bspause,
            "shotInterval": self.dcb.score_shotpause,
            "jab": self.dcb.score_jab,
            "followThrough": self.dcb.score_followthru,
            "tipSteer": self.dcb.score_steering,
            "straightness": self.dcb.score_straightness,
            "finesse": self.dcb.threshold_power,
            "finish": self.dcb.score_freeze,
            "timeStamp": datetime.datetime.utcnow().isoformat(),
            "trainer": {
                "username": self.trainer['username'].encode('utf-8')
            },
            "player": {
                "username": self.player['username'].encode('utf-8')
            },
            "xyzShots": self.xyz_shots
        })
        
        file = open('hola.json', 'w+')
        file.write(payload)

        response = requests.post(self.api_url("/shots"), data=payload, headers=HEADER)

        if response.status_code == 201:
            print("Shot successfuly saved")
        else:
            print("%s - %s" % (response.status_code, response.reason))
    
    def api_url(self, url):
        s = "%s%s" % (API_BASE_URL, url)
        print(s)
        return s
