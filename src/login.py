import sys
import requests
from chooseplayer import *

if sys.version_info[0] < 3:
    import Tkinter as Tk
    import ttk
else:
    import tkinter as Tk
    from tkinter import ttk, tkMessageBox

API_BASE_URL = "https://mocktesisasobiguaapi.azurewebsites.net/v1"
# API_BASE_URL = "https://localhost:5001/v1"
HEADER = {"Content-Type": "application/json", "Accept": "*"}

class Login():
    def __init__(self):
        self.root = Tk.Tk()
        self.root.title("CDAG - ASOBIGUA")
        lbl = Tk.Label(self.root, text = "Usuario:")
        lbl.grid(row = 0, column = 0)
        self.txbUsername = Tk.Entry(self.root)
        self.txbUsername.grid(row = 0, column = 1)

        lbl = Tk.Label(self.root, text = "Password:")
        lbl.grid(row = 1, column = 0)
        self.txbPassword = Tk.Entry(self.root, show = "*")
        self.txbPassword.grid(row = 1, column = 1)

        self.loginButton = Tk.Button(self.root, text = "Iniciar sesion", command = self.login)
        self.loginButton.grid(row = 2, column = 1)

        self.lblLoginResult = Tk.Label(self.root)
        self.lblLoginResult.grid(row = 3, column = 1)

        Tk.mainloop()

    def api_url(self, url):
        s = "%s%s" % (API_BASE_URL, url)
        print(s)
        return s

    def login(self):
        username = self.txbUsername.get()
        password = self.txbPassword.get()

        payload = str({
            "username": username,
            "password": password
        })

        response = requests.post(self.api_url("/users/login"), data=payload, headers=HEADER)

        if response.status_code != 200:
            self.lblLoginResult.config(text = response.reason)
            return

        self.lblLoginResult.config(text = "")
        self.trainer = response.json()
        self.root.destroy()
        if self.trainer['userType'] == 'Trainer':
            choose = ChoosePlayer(self.trainer)
            self.player = choose.player
        else:
            self.player = self.trainer
        
        print(self.trainer)
        print(self.player)

def main():
    login = Login()

if __name__ == '__main__':
    main()