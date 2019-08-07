import serial
import serialport
import time
import serial.tools.list_ports as list_ports

import sys
if sys.version_info[0] < 3:
    import Tkinter as Tk
else:
    import tkinter as Tk


def find_serial_port(vid, pid):
    ports = list(list_ports.comports())
    for port in ports:
        if port[2].find(vid) > 0 and port[2].find(pid) > 0:
            return port


def _test():
    port = find_serial_port("2458", "0001")  # VID = '2458', PID = '0001'
    if port is None:
        print "Dispositivo Bluetooth compatible con DigiCue no encontrado."
    else:
        s = serial.Serial(port[0])
        s.close()
        print "Exito"


class SerialPortSelect:

    def __init__(self, master):
        self.master = master
        master.resizable(0, 0)

        self.label_text = Tk.StringVar()
        self.label_text.set("Seleccione el puerto Bluetooth para conectar el DigiCue:")
        self.label = Tk.Label(master, textvariable=self.label_text)
        self.label.pack()
        self.portref = []
        self.ports = None
        print [[item for item in comport] for comport in serialport.list_ports.comports()]
        self.ports = list(serialport.list_ports.comports())
        print serialport.list_ports.comports()
        print self.ports

        master.title("Seleccione el puerto serial")
        self.listbox = Tk.Listbox(master, width=100)
        self.listbox.pack()
        self.button = Tk.Button(
            master,
            text="OK",
            width=5,
            command=self.button_action)
        self.button.pack()
        self.listbox.insert(Tk.END)
        for item in self.ports:
            text = ""
            for subitem in item:
                if len(text) > 0:
                    text = "%s - %s" % (text, subitem)
                    print text
                else:
                    text = subitem
                    self.portref.append(subitem)
            self.listbox.insert(Tk.END, text)

        master.mainloop()

    def button_action(self):
        try:
            index = int(self.listbox.curselection()[0])
        except IndexError:
            return

        try:
            f = open("comport.cfg", "w")
            f.write(self.portref[index])
            f.close()
            self.label_text.set(
                "Exito. %s guardado como puerto Bluetooth para el DigiCue." %
                self.portref[index])
        except BaseException:
            self.label_text.set(
                "Error al guardar la configuracion. Chequee los permisos.")


def launch_selection():
    root = Tk.Tk()
    select = serialport.SerialPortSelect(root)


if __name__ == "__main__":
    launch_selection()
