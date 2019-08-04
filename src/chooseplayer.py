import sys
import requests

if sys.version_info[0] < 3:
    import Tkinter as Tk
    import ttk
else:
    import tkinter as Tk
    from tkinter import ttk, tkMessageBox

API_BASE_URL = "https://mocktesisasobiguaapi.azurewebsites.net/v1"
# API_BASE_URL = "https://localhost:5001/v1"
HEADER = {"Content-Type": "application/json", "Accept": "*"}

class ChoosePlayer():
    def __init__(self, trainer):
        self.listOfPlayers = self.getListOfPlayers()
        self.trainer = trainer
        self.root = Tk.Tk()
        self.root.title("CDAG - ASOBIGUA")
        lbl = Tk.Label(self.root, text="Escoger jugador a entrenar:")
        lbl.pack()

        self.listPlayers = Tk.Listbox(self.root, width = 75, height=25)
        self.listPlayers.pack()
        for item in self.listOfPlayers:
            self.listPlayers.insert(Tk.END, "%s, %s (%s)" % (item['lastName'], item['name'], item['username']))
        
        btnChoosePlayer = Tk.Button(self.root, text="Escoger Jugador", command=self.btnChoosePlayerClick)
        btnChoosePlayer.pack()

        self.root.mainloop()

    def api_url(self, url):
        s = "%s%s" % (API_BASE_URL, url)
        print(s)
        return s

    def getListOfPlayers(self):
        payload = {"usertype": "players"}
        response = requests.get(self.api_url("/users"), params=payload)
        if response.status_code == 200:
            return response.json()
        return None

    def btnChoosePlayerClick(self):
        selected = self.listPlayers.curselection()[0]
        self.player = self.listOfPlayers[selected]
        self.root.destroy()

def main():
    choose = ChoosePlayer(None)

if __name__ == '__main__':
    main()