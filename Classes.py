import wx
import wx.stc

import argon2
import binascii
# from argon2 import PasswordHasher, Type
import random
import json
from json import JSONEncoder
import sys
# from PyQt5.QtWidgets import QApplication, QWidget, QTreeView, QFileSystemModel, QVBoxLayout
# from PyQt5.QtCore import QModelIndex


import io
import os
import sys
import operator
import contextlib

# from PyQt5.QtCore import (qVersion, QEventLoop, QDataStream, QByteArray,
#                           QIODevice, QSaveFile)
# from PyQt5.QtWidgets import QApplication

# from qutebrowser.utils import log

APP_SIZE_X = 400
APP_SIZE_Y = 500
Username = ""
Password = ""
currentManager = None
fileName = ""
file_formats = ["exe", "txt", "csv", "json", "xml",    "png",    "jpg",    "pdf",    "mp3",    "xlsx",    "xlsm",    "xlsb",    "db",    "sqlite",    "html",    "htm",    "yml",    "yaml",    "ini",    "cfg",    "conf",    "zip",    "tar",    "gz",    "py",    "pyc",    "pyd",    "pkl",    "pickle",    "jpeg",
                "gif",    "bmp",    "svg",    "ico",    "mp4",    "wav",    "ogg",    "flac",    "avi",    "mov",    "wmv",    "mkv",    "doc",    "docx",    "ppt",    "pptx",    "odt",    "ods",    "odp",    "epub",    "md",    "rst",    "tex",    "bz2",    "rar",    "7z",    "ipynb",    "php",    "js",    "css",    "toml"]
copiedFileName = ""


class Manager():
    def __init__(self, name, privileges):
        self.name = name
        self.privileges = privileges


class FileDialog(wx.Frame):

    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title,
                          size=(APP_SIZE_X, APP_SIZE_Y))

        font = wx.Font(20, family=wx.FONTFAMILY_MODERN, style=0, weight=90,
                       underline=False, faceName="", encoding=wx.FONTENCODING_DEFAULT)

        self.header = wx.StaticText(self, label="Get a file:", pos=(60, 40))
        self.header.SetFont(font)

        self.name_header = wx.StaticText(
            self, label=":Enter file name", pos=(210, 100))
        self.name = wx.TextCtrl(self, value="",
                                pos=(50, 100), size=(140, -1))

        self.newName_header = wx.StaticText(
            self, label="Enter new name:", pos=(192, 140))
        self.newName = wx.TextCtrl(
            self, value="", pos=(50, 140), size=(140, -1), id=3)

        self.feedback_header = wx.StaticText(self, label="", pos=(120, 300))

        wx.Button(self, 2, 'Confirm', (105, 200))
        wx.Button(self, 1, 'Close', (105, 400))

        self.Bind(wx.EVT_BUTTON, self.OnConfirm, id=2)
        self.Bind(wx.EVT_BUTTON, self.OnClose, id=1)

        self.Centre()
        self.Show()

    def OnConfirm(self, event):
        global fileName, copiedFileName
        fileName = self.name.Value
        copiedFileName = self.newName.Value
        found = False
        # Check file validation
        parts = fileName.split(".")
        copy_parts = copiedFileName.split(".")
        if (len(parts) > 1 and len(copy_parts) > 1):

            for f in file_formats:
                if (parts[len(parts)-1] == f):
                    found = True
                    break
            if (not found):
                self.feedback_header.SetLabel(
                    "This file format is not valid or not supported")
            elif (copy_parts[1] != parts[1]):
                self.feedback_header.SetLabel(
                    "Enter the same file formats")
            else:
                self.Destroy()
        else:
            self.feedback_header.SetLabel(
                "This file format is not valid or not supported")

    def OnClose(self, event):
        self.Destroy()


class SignUp(wx.Frame):

    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title,
                          size=(APP_SIZE_X, APP_SIZE_Y))

        font = wx.Font(20, family=wx.FONTFAMILY_MODERN, style=0, weight=90,
                       underline=False, faceName="", encoding=wx.FONTENCODING_DEFAULT)

        self.header = wx.StaticText(self, label="Sign In:", pos=(60, 40))
        self.header.SetFont(font)

        self.name_header = wx.StaticText(
            self, label=":Enter Name", pos=(210, 100))
        self.name = wx.TextCtrl(self, value="",
                                pos=(50, 100), size=(140, -1))

        self.pass_header = wx.StaticText(
            self, label=":Enter Password", pos=(192, 140))
        self.password = wx.TextCtrl(
            self, value="", pos=(50, 140), size=(140, -1), id=3)

        self.feedback_header = wx.StaticText(self, label="", pos=(120, 300))

        wx.Button(self, 2, 'Confirm', (105, 200))
        wx.Button(self, 1, 'Close', (105, 400))

        # wx.Button(self, 2, 'Confirm', (105, 400))
        # self.Bind(wx.EVT_BUTTON, lambda event: self.OnConfirm(event), b)
        self.Bind(wx.EVT_BUTTON, self.OnConfirm, id=2)
        # self.Bind(wx.EVT_KEY_DOWN, self.KeyPress, id=3)
        self.Bind(wx.EVT_BUTTON, self.OnClose, id=1)

        self.Centre()
        self.Show()

    def KeyPress(self, event):
        print(event)

    def OnClose(self, event):
        self.Destroy()

    def gen_salt(self):  # create a unique salt to the passowrd
        salt = ""
        for i in range(10):
            char = random.randint(33, 126)
            salt += chr(char)
        return salt

    def HandleIdentification(self):
        HASH_PEPPER = "Aa5!gGpR"
        # password P: the password (or message) to be hashed
        # salt S: random-generated salt(16 bytes recommended for password hashing)
        # iterations t: number of iterations to perform
        # memorySizeKB m: amount of memory ( in kilobytes) to use
        # parallelism p: degree of parallelism(i.e. number of threads)
        # outputKeyLength T: desired number of returned bytes

        userSalt = self.gen_salt()
        # Try to open the users database
        try:
            f = open("Users.txt", "r+")
        except:
            f = open("Users.txt", "w+")
        # Check if it's empty
        credentials = f.read()
        if (credentials == ""):
            if (Username == "" or Password == ""):
                return "One of the fields is empty"
            passwordHashRaw = argon2.hash_password_raw(
                time_cost=16, memory_cost=2**15, parallelism=2, hash_len=32,
                password=(HASH_PEPPER + Password).encode(), salt=userSalt.encode(), type=argon2.low_level.Type.ID)
            passwordHash = binascii.hexlify(passwordHashRaw).decode()
            print("Argon2 raw hash:", passwordHash)
            with open("Users.txt", "w") as f:
                # name,passwordHash,salt,privileges
                f.write(f"{Username}~{passwordHash}~{userSalt}~{1}\n")
                return Manager(Username, 1)
        else:
            credentials = credentials.split("\n")

            found = -1
            # Iterate over all the users and check if the user exists
            for i in range(len(credentials)-1):
                if (found == -1):
                    # username~passwordHash~salt~priveleges
                    info = credentials[i].split("~")
                    if (info[0] == Username):
                        passwordHashRaw = argon2.hash_password_raw(
                            time_cost=16, memory_cost=2**15, parallelism=2, hash_len=32,
                            password=(HASH_PEPPER + Password).encode(), salt=info[2].encode(), type=argon2.low_level.Type.ID)
                        passwordHash = binascii.hexlify(
                            passwordHashRaw).decode()
                        # Password is correct
                        if (info[1] == passwordHash):
                            found = i

                        # Password is incorrect
                        else:
                            return "Password is incorrect"

                else:
                    break
            if (found != -1):
                if (Username == "" or Password == ""):
                    return "One of the fields is empty"
                # Create the manager and return it
                info = credentials[i].split("~")
                return Manager(info[0], int(info[3]))
            # Register
            passwordHashRaw = argon2.hash_password_raw(
                time_cost=16, memory_cost=2**15, parallelism=2, hash_len=32,
                password=(HASH_PEPPER + Password).encode(), salt=userSalt.encode(), type=argon2.low_level.Type.ID)
            passwordHash = binascii.hexlify(passwordHashRaw).decode()
            with open("Users.txt", "a") as f:
                # name,passwordHash,salt,privileges
                f.write(f"{Username}~{passwordHash}~{userSalt}~{1}\n")
                return Manager(Username, 1)

    def OnConfirm(self, event):
        global Username, Password, currentManager
        Username = self.name.Value
        Password = self.password.Value
        retVal = self.HandleIdentification()
        if (retVal != "One of the fields is empty" and retVal != "Password is incorrect"):
            currentManager = retVal
            self.Destroy()
        else:
            self.feedback_header.SetLabel(retVal)
