import tkinter as tk
from login import Login_App

loginWindow = tk.Tk()

# login windows vars
loginWin = Login_App.loginInit(loginWindow)
loginWindow.mainloop()
