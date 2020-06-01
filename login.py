import tkinter as tk
from tkinter import messagebox
from main_dash import Main_Dashboard
import os
import json, hashlib


class Login_App:
    @classmethod
    def loginInit(cls, master):
        __appPath = ".keeper"
        # get user path
        __path = os.environ["USERPROFILE"]
        # set working dir
        os.chdir(__path)
        # check if path exists
        if os.path.exists(__appPath):
            # return cls(master, "OK")
            cls.make_config(master, __path, True)
        else:
            try:
                os.mkdir(__appPath)  # make the dir
                # return cls(master, "OK")
                cls.make_config(master, __path, True)
            except Exception as e:
                return cls(master, e)

    @classmethod
    def make_config(cls, master, path, dir_log):
        # config vars
        __path_CONFIG = path + "\\.keeper\\" + "config.json"
        __config = {"password": "0192023a7bbd73250516f069df18b500"}
        # make the config file if it is missing
        try:
            if dir_log:
                if os.path.exists(__path_CONFIG):
                    pass
                else:
                    config_file = open(__path_CONFIG, "w")
                    config_file.write(json.dumps(__config, indent=4))
                    config_file.close()
            fileLog = json.loads(open(__path_CONFIG, "r").read())
            __pwd = fileLog["password"]
            initStatus = True
        except Exception as e:
            initStatus = e
        # return the vals to the __init__
        return cls(master, initStatus, __pwd)

    def __init__(self, master, initStatus, __master_pass):
        self.master = master
        self.initStatus = initStatus
        self.__master_pass = __master_pass  # get the master password
        # check if initialization is success or not
        if self.initStatus:
            # set app vars
            self.master.title("Login - Keeper")
            self.master.geometry("400x200")
            self.master.resizable(width=False, height=False)

            ## Components
            # header
            label1 = tk.Label(
                self.master,
                text="Login - Keeper",
                fg="#283142",
                font=["Segoe UI Black", 25],
            )
            label2 = tk.Label(
                self.master,
                text="Please enter your Admin PASSWORD.",
                font=["Segoe UI", 12],
            )
            label1.pack()
            label2.pack()

            # form
            formFrame = tk.Frame(self.master)
            formFrame.pack(pady=5)

            self.loginPass = tk.StringVar()

            self.tbPass = tk.Entry(
                formFrame,
                width=27,
                justify="center",
                show="*",
                font=["Segoe UI Bold", 11],
                textvariable=self.loginPass,
            )
            # bind enter key from keyboard
            self.tbPass.bind("<Return>", (lambda event: self.__login()))
            btnLogin = tk.Button(
                formFrame,
                text="LOGIN",
                fg="white",
                bg="#1C93EF",
                font=["Segoe UI Bold", 10],
                width=20,
                pady=5,
                command=lambda: self.__login(),
            )
            self.tbPass.pack(ipady=5, pady=5)
            self.tbPass.focus()
            btnLogin.pack(pady=5, ipady=5)
        else:
            messagebox.showerror("Error!", "An error has occured.\n" + e)

    def __login(self):
        __entered = self.loginPass.get()
        # check if input is empty or not
        if len(__entered) == 0:
            messagebox.showinfo(
                "No Password!", "Please enter your administrator password to login."
            )
        else:
            __entered_pass = hashlib.md5(__entered.encode())
            # check login password if correct or not
            if self.__master_pass == __entered_pass.hexdigest():
                # remove the text in the entry box
                self.tbPass.delete(0, tk.END)
                # hide login window
                self.master.withdraw()
                # show dashboard window
                __logMeIn = Main_Dashboard.initialize(self)
            else:
                messagebox.showerror(
                    "Incorrect Password!",
                    "The administrator password you've entered is incorrect!",
                )

    # reload the master pass from the config.json
    def __reload_MasterPass(self):
        with open(os.environ["USERPROFILE"] + "\\.keeper\\config.json") as f:
            __mp = json.load(f)

        self.__master_pass = __mp["password"]

    def _show(self):
        # reload the master password
        self.__reload_MasterPass()

        # show the login window if main dashboard is closed or logged out
        self.master.update()
        self.master.deiconify()
