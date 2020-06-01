import tkinter as tk
from tkinter import messagebox
import os, json
import hashlib


class Account_Settings(tk.Toplevel):
    @classmethod
    def account_Settings(cls, main_form):
        __config_data = os.environ["USERPROFILE"] + "\\.keeper\\config.json"

        return cls(main_form, __config_data)

    def __init__(self, main_form, config_data):
        self.main_form = main_form
        self.__config_data = config_data

        tk.Toplevel.__init__(self)

        self.geometry("400x160")
        self.title("Change ADMIN Password - Keeper")
        self.resizable(width=False, height=False)

        label1 = tk.Label(
            self,
            text="Change ADMIN Passwod",
            fg="#283142",
            font=["Segoe UI Black", 16],
        )
        label1.pack()

        label2 = tk.Label(
            self, text="Enter New Password", font=["Century Gothic Bold", 11]
        )
        label2.pack(anchor=tk.W, padx=20, pady=5)

        self.entry_NewPass = tk.StringVar()
        tbEnt_NewPass = tk.Entry(
            self,
            width=25,
            justify="center",
            font=["Century Gothic", 9],
            textvariable=self.entry_NewPass,
        )
        tbEnt_NewPass.pack(ipady=3)

        btnChangePass = tk.Button(
            self,
            text="Change Password",
            bg="#159F5C",
            fg="white",
            font=["Century Gothic", 9],
            command=lambda: self.__update_AdminPass(),
        )
        btnChangePass.pack(ipady=5, ipadx=3, pady=5)

    def __Get_EntryNewPass(self):
        return self.entry_NewPass.get()

    def __update_AdminPass(self):
        if len(self.__Get_EntryNewPass()) == 0:
            messagebox.showinfo(
                "No Password SET",
                "Please enter a New Password to update the Admin account.",
            )
        else:
            __confirm_change = messagebox.askokcancel(
                "Update ADMIN Password?",
                "This will update the current Administrator password set for this program.\n  Warning: This cannot be undone.\n  Confirm?",
            )
            if __confirm_change:
                try:
                    with open(self.__config_data, "r") as f:
                        __config_data = json.load(f)

                        __config_data["password"] = self.__hash_NewPass(
                            self.__Get_EntryNewPass()
                        )
                    with open(self.__config_data, "w") as f:
                        f.write(json.dumps(__config_data))

                    messagebox.showinfo(
                        "Update SUCCESS!",
                        "The Administrator password has been successfully updated.",
                    )

                    # destroy this window and focus on the main form
                    self.destroy()
                    self.main_form._show_MainForm()
                except Exception as e:
                    messagebox.showerror(
                        "Error Updating!",
                        "An error has occured while updating the Administrator password.\n"
                        + str(e),
                    )

    def __hash_NewPass(self, raw_new_pass):
        __hash_pass = hashlib.md5(raw_new_pass.encode())

        return __hash_pass.hexdigest()
