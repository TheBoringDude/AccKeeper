import tkinter as tk
import pandas as pd
from tkinter import messagebox, ttk
import os, csv

# copied from https://gist.github.com/novel-yet-trivial/2841b7b640bba48928200ff979204115
class DoubleScrolledFrame:
    """
    A vertically scrolled Frame that can be treated like any other Frame
    ie it needs a master and layout and it can be a master.
    keyword arguments are passed to the underlying Frame
    except the keyword arguments 'width' and 'height', which
    are passed to the underlying Canvas
    note that a widget layed out in this frame will have Canvas as self.master,
    if you subclass this there is no built in way for the children to access it.
    You need to provide the controller separately.
    """

    def __init__(self, master, **kwargs):
        width = kwargs.pop("width", None)
        height = kwargs.pop("height", None)
        self.outer = tk.Frame(master, **kwargs)

        self.vsb = ttk.Scrollbar(self.outer, orient=tk.VERTICAL)
        self.vsb.grid(row=0, column=1, sticky="ns")
        self.hsb = ttk.Scrollbar(self.outer, orient=tk.HORIZONTAL)
        self.hsb.grid(row=1, column=0, sticky="ew")
        self.canvas = tk.Canvas(
            self.outer, highlightthickness=0, width=width, height=height
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.outer.rowconfigure(0, weight=1)
        self.outer.columnconfigure(0, weight=1)
        self.canvas["yscrollcommand"] = self.vsb.set
        self.canvas["xscrollcommand"] = self.hsb.set
        # mouse scroll does not seem to work with just "bind"; You have
        # to use "bind_all". Therefore to use multiple windows you have
        # to bind_all in the current widget
        self.canvas.bind("<Enter>", self._bind_mouse)
        self.canvas.bind("<Leave>", self._unbind_mouse)
        self.vsb["command"] = self.canvas.yview
        self.hsb["command"] = self.canvas.xview

        self.inner = tk.Frame(self.canvas)
        # pack the inner Frame into the Canvas with the topleft corner 4 pixels offset
        self.canvas.create_window(4, 4, window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", self._on_frame_configure)

        self.outer_attr = set(dir(tk.Widget))

    def __getattr__(self, item):
        if item in self.outer_attr:
            # geometry attributes etc (eg pack, destroy, tkraise) are passed on to self.outer
            return getattr(self.outer, item)
        else:
            # all other attributes (_w, children, etc) are passed to self.inner
            return getattr(self.inner, item)

    def _on_frame_configure(self, event=None):
        x1, y1, x2, y2 = self.canvas.bbox("all")
        height = self.canvas.winfo_height()
        width = self.canvas.winfo_width()
        self.canvas.config(scrollregion=(0, 0, max(x2, width), max(y2, height)))

    def _bind_mouse(self, event=None):
        self.canvas.bind_all("<4>", self._on_mousewheel)
        self.canvas.bind_all("<5>", self._on_mousewheel)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mouse(self, event=None):
        self.canvas.unbind_all("<4>")
        self.canvas.unbind_all("<5>")
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        """Linux uses event.num; Windows / Mac uses event.delta"""
        func = self.canvas.xview_scroll if event.state & 1 else self.canvas.yview_scroll
        if event.num == 4 or event.delta > 0:
            func(-1, "units")
        elif event.num == 5 or event.delta < 0:
            func(1, "units")


class Main_Dashboard(tk.Toplevel):
    @classmethod
    def initialize(cls, parent):
        __working_dir = os.environ["USERPROFILE"] + "\\.keeper\\"
        __accs_path = ".accounts"

        os.chdir(__working_dir)

        if not os.path.exists(__accs_path):
            os.mkdir(__accs_path)

        # set the new working dir
        __new_working_dir = __working_dir + ".accounts"

        __acc_file = __new_working_dir + "\\accounts.csv"
        # make the accounts file if missing
        if not os.path.isfile(__acc_file):
            __make_file = open(__acc_file, "w+")
            __make_file.close

        cls.__write_InitData(__acc_file)

        __accounts = pd.read_csv(__acc_file).iloc[::-1]

        # return the parent form and the accounts dataframe
        return cls(parent, __accounts)

    # write base accounts.csv file
    @classmethod
    def __write_InitData(cls, accs_file):
        __f_Accs = open(accs_file, "w")

        # write headers to csv file
        __init_Writer = csv.DictWriter(
            __f_Accs, fieldnames=["UnameEmail", "Password", "Website"]
        )
        __init_Writer.writeheader()

        __f_Accs.close()

    def __init__(self, parent, acc_list):
        # get data from initialize
        self.acc_list = acc_list
        self.parent_frame = parent

        tk.Toplevel.__init__(self)

        self.__font = "Century Gothic"

        self.geometry("500x600")
        self.title("Keeper - Offline Account Saver")
        self.protocol("WM_DELETE_WINDOW", self.__onClose)
        self.resizable(width=False, height=False)

        ### TOP Frame
        topFrame = tk.Frame(self)
        topFrame.pack()

        label1 = tk.Label(
            self,
            text="Keeper - OFFLINE Account Saver",
            fg="#283142",
            font=["Segoe UI Black", 20],
        )
        label1.pack()

        ## Add Account
        addAccFrame = tk.Frame(self)
        addAccFrame.pack(pady=5)

        lblAddAccs = tk.Label(
            addAccFrame,
            text="Add New Account",
            font=[self.__font + " Bold", 10, "underline"],
        )
        lblUnameEmail = tk.Label(
            addAccFrame, text="Uname/Email:", font=[self.__font, 11]
        )
        lblPass = tk.Label(addAccFrame, text="Password:", font=[self.__font, 11])
        lblWebsite = tk.Label(addAccFrame, text="Website:", font=[self.__font, 11])

        self.e_UnameEmail = tk.StringVar()
        self.e_Password = tk.StringVar()
        self.e_Website = tk.StringVar()
        self.tbUnameEmail = tk.Entry(
            addAccFrame,
            width=30,
            font=[self.__font, 11],
            textvariable=self.e_UnameEmail,
        )
        self.tbPass = tk.Entry(
            addAccFrame, width=30, font=[self.__font, 11], textvariable=self.e_Password
        )
        self.tbWebsite = tk.Entry(
            addAccFrame, width=30, font=[self.__font, 11], textvariable=self.e_Website
        )

        btnAddAcc = tk.Button(
            addAccFrame,
            text="Add Account",
            width=20,
            fg="white",
            bg="#0078D7",
            font=[self.__font, 10],
            command=lambda: self.__update_data(),
        )

        lblAddAccs.grid(row=0, columnspan=2, pady=3)
        lblUnameEmail.grid(row=1, column=0)
        lblPass.grid(row=2, column=0)
        lblWebsite.grid(row=3, column=0)
        self.tbUnameEmail.grid(row=1, column=1, ipady=3, pady=2)
        self.tbPass.grid(row=2, column=1, ipady=3, pady=2)
        self.tbWebsite.grid(row=3, column=1, ipady=3, pady=2)
        btnAddAcc.grid(row=4, columnspan=2, ipady=5, ipadx=5, pady=2)

        ## Accounts Frame
        self.accsFrame = DoubleScrolledFrame(self)
        tk.Label(
            self.accsFrame,
            text="ACCOUNTS:",
            anchor="w",
            font=[self.__font + " Bold", 12],
        ).grid(sticky=tk.W, row=0, columnspan=3)
        tk.Label(
            self.accsFrame,
            text="Uname/Email",
            fg="#1A2032",
            font=[self.__font + " Bold", 11],
        ).grid(row=1, column=1, pady=5, padx=35)
        tk.Label(
            self.accsFrame,
            text="Password",
            fg="#1A2032",
            font=[self.__font + " Bold", 11],
        ).grid(row=1, column=3, pady=5, padx=35)
        tk.Label(
            self.accsFrame,
            text="Website",
            fg="#1A2032",
            font=[self.__font + " Bold", 11],
        ).grid(row=1, column=5, pady=5, padx=35)

        # add a separators
        ttk.Separator(self.accsFrame, orient=tk.VERTICAL).grid(
            column=2, row=1, sticky="ns"
        )
        ttk.Separator(self.accsFrame, orient=tk.VERTICAL).grid(
            column=4, row=1, sticky="ns"
        )

        ttk.Separator(self.accsFrame, orient=tk.HORIZONTAL).grid(
            column=1, row=1, sticky="sew"
        )
        ttk.Separator(self.accsFrame, orient=tk.HORIZONTAL).grid(
            column=3, row=1, sticky="sew"
        )
        ttk.Separator(self.accsFrame, orient=tk.HORIZONTAL).grid(
            column=5, row=1, sticky="sew"
        )

        # plot the data
        self.__load_data()

        self.accsFrame.pack(pady=5, expand=tk.TRUE, fill=tk.BOTH, padx=10)

        ### BOTTOM Frame
        bottomFrame = tk.Frame(self)
        bottomFrame.pack(pady=5, expand=tk.TRUE, fill=tk.BOTH, padx=20)

        btnChangeAccPass = tk.Button(
            bottomFrame,
            text="Change Account Password",
            font=[self.__font, 10],
            bg="#3F4F60",
            command=lambda: self.__show_ChangePass(),
        )
        btnChangeAccPass.pack(side=tk.LEFT, ipady=5, ipadx=5)

        btnLogout = tk.Button(
            bottomFrame,
            text="Logout",
            pady=5,
            font=[self.__font, 9],
            command=lambda: self.__logout(),
        )
        btnLogout.pack(side=tk.RIGHT)

    # show change pass window
    def __show_ChangePass(self):
        from settings import Account_Settings

        __change_pass = Account_Settings.account_Settings(self)
        # focus on the change acc password
        __change_pass.grab_set()
        __change_pass.focus_force()

    # get the UnameEmail from the csv
    def __get_acc_unameEmail(self):
        __acc_UnameEmail = self.acc_list["UnameEmail"]
        return __acc_UnameEmail

    # get the Password from the csv
    def __get_acc_pass(self):
        __acc_Pass = self.acc_list["Password"]
        return __acc_Pass

    # get the Website from the csv
    def __get_acc_website(self):
        __acc_Website = self.acc_list["Website"]
        return __acc_Website

    # collect the data
    def __col_data(self):
        list_data = [
            self.e_UnameEmail.get(),
            self.e_Password.get(),
            self.e_Website.get(),
        ]
        return list_data

    ## UPDATE THE accounts.csv
    def __update_data(self):
        __new_acc = self.__col_data()

        try:
            with open(
                os.environ["USERPROFILE"] + "\\.keeper\\.accounts\\accounts.csv", "a"
            ) as fd:
                __writer = csv.writer(fd)
                __writer.writerow(__new_acc)

            messagebox.showinfo(
                "Update Success!", "The account has been added to the database."
            )

            # remove the text from the textbox
            self.tbUnameEmail.delete(0, tk.END)
            self.tbPass.delete(0, tk.END)
            self.tbWebsite.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror(
                "Update Data Error!",
                "An error has occured while updating the database.\n" + str(e),
            )

        self.__reload_data()

    # load the data and plot to the grid
    def __load_data(self):
        n = 2  # counter for rows
        for uemail, pwd, weburl in zip(
            self.__get_acc_unameEmail(), self.__get_acc_pass(), self.__get_acc_website()
        ):
            try:
                tk.Label(self.accsFrame, text=uemail, font=[self.__font, 10]).grid(
                    row=n, column=1, padx=5
                )
                tk.Label(self.accsFrame, text=pwd, font=[self.__font, 10]).grid(
                    row=n, column=3, padx=5
                )
                tk.Label(self.accsFrame, text=weburl, font=[self.__font, 10]).grid(
                    row=n, column=5, padx=5
                )

                # add vertical separator
                ttk.Separator(self.accsFrame, orient=tk.VERTICAL).grid(
                    column=2, row=n, sticky="ns"
                )
                ttk.Separator(self.accsFrame, orient=tk.VERTICAL).grid(
                    column=4, row=n, sticky="ns"
                )

                # add horizontal separator
                ttk.Separator(self.accsFrame, orient=tk.HORIZONTAL).grid(
                    column=1, row=n, sticky="sew"
                )
                ttk.Separator(self.accsFrame, orient=tk.HORIZONTAL).grid(
                    column=3, row=n, sticky="sew"
                )
                ttk.Separator(self.accsFrame, orient=tk.HORIZONTAL).grid(
                    column=5, row=n, sticky="sew"
                )
                n += 1
            except Exception as e:
                messagebox.showerror(
                    "Data Error!",
                    "There was a problem when loading the accounts database.",
                )

    # reinitialize data
    def __reload_data(self):
        __new_Data = os.environ["USERPROFILE"] + "\\.keeper\\.accounts\\accounts.csv"
        self.acc_list = pd.read_csv(__new_Data).iloc[::-1]

        self.__load_data()

    # button logout is clicked / clicked ok on messagebox quit
    def __logout(self):
        self.destroy()
        self.parent_frame._show()

    # if close window button is clicked
    def __onClose(self):
        if messagebox.askokcancel(
            "Quit", "Do you want to quit?\nYou will be logged out of your account."
        ):
            self.__logout()

    def _show_MainForm(self):
        self.focus()
