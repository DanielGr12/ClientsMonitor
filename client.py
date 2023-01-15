from email import header
from pydoc import cli
from socket import socket
from turtle import width
from zlib import decompress, compress
from mss import mss

import mouse
import pygame
import wx
import hashlib
import random
# from Crypto.Cipher import AES
# from Crypto import Random
import base64
import pyautogui
import sys


class Register(wx.Dialog):
    def __init__(self, parent, id, title, sock):
        wx.Dialog.__init__(self, parent, id, title,
                           size=(APP_SIZE_X, APP_SIZE_Y))

        font = wx.Font(20, family=wx.FONTFAMILY_MODERN, style=0, weight=90,
                       underline=False, faceName="", encoding=wx.FONTENCODING_DEFAULT)

        self.header = wx.StaticText(self, label=":Register", pos=(60, 40))
        self.header.SetFont(font)

        self.name_header = wx.StaticText(
            self, label=":Enter Name", pos=(210, 100))
        self.name = wx.TextCtrl(self, value="Enter name",
                                pos=(50, 100), size=(140, -1))

        self.pass_header = wx.StaticText(
            self, label=":Enter Password", pos=(192, 140))
        self.password = wx.TextCtrl(
            self, value="Enter password", pos=(50, 140), size=(140, -1))

        self.feedback_header = wx.StaticText(self, label="", pos=(120, 300))

        b = wx.Button(self, 2, 'Confirm', (105, 200))
        wx.Button(self, 1, 'Close', (105, 400))

        self.Bind(wx.EVT_BUTTON, lambda event: self.OnConfirm(event, sock), b)
        self.Bind(wx.EVT_BUTTON, self.OnClose, id=1)

        self.Centre()
        self.ShowModal()

    def OnClose(self, event):
        self.Destroy()

    def OnConfirm(self, event, sock):
        sock.send(f"{self.name.Value}~{self.password.Value}".encode())
        self.Destroy()


class Login(wx.Dialog):
    def __init__(self, parent, id, title, sock):
        wx.Dialog.__init__(self, parent, id, title,
                           size=(APP_SIZE_X, APP_SIZE_Y))

        font = wx.Font(20, family=wx.FONTFAMILY_MODERN, style=0, weight=90,
                       underline=False, faceName="", encoding=wx.FONTENCODING_DEFAULT)

        self.header = wx.StaticText(self, label=":Enter Info", pos=(60, 40))
        self.header.SetFont(font)

        self.name_header = wx.StaticText(
            self, label=":Enter Name", pos=(210, 100))
        self.name = wx.TextCtrl(self, value="Enter name",
                                pos=(50, 100), size=(140, -1))

        self.pass_header = wx.StaticText(
            self, label=":Enter Password", pos=(192, 140))
        self.password = wx.TextCtrl(
            self, value="Enter password", pos=(50, 140), size=(140, -1))

        self.feedback_header = wx.StaticText(self, label="", pos=(120, 300))

        b = wx.Button(self, 2, 'Confirm', (105, 200))
        wx.Button(self, 1, 'Close', (105, 400))

        self.Bind(wx.EVT_BUTTON, lambda event: self.OnConfirm(event, sock), b)
        self.Bind(wx.EVT_BUTTON, self.OnClose, id=1)

        self.Centre()
        self.ShowModal()

    def OnClose(self, event):
        self.Destroy()

    def OnConfirm(self, event, sock):
        sock.send(f"{self.name.Value}~{self.password.Value}".encode())
        data = sock.recv(1024)
        if data != b"correct":
            self.feedback_header.SetLabel("Wrong")
            print("Wrong!")
        else:
            print("Hello!")
            self.Destroy()


APP_SIZE_X = 300
APP_SIZE_Y = 500
width, height = pyautogui.size()
width -= 1
height -= 30

keyboard_action = "nothing"
mouse_action = "nothing"

mouseAndKeyboard = False


BS = 16
def pad(s): return s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
def unpad(s): return s[:-ord(s[len(s)-1:])]


def retreive_screenshot(cli_sock):  # ,key
    with mss() as sct:
        # The region to capture
        rect = {'top': 0, 'left': 0, 'width': width, 'height': height}
        try:
            while 'recording':

                # Capture the screen
                img = sct.grab(rect)
                # Tweak the compression level here (0-9)
                pixels = compress(img.rgb, 6)

                # Send the size of the pixels length
                size = len(pixels)
                size_len = (size.bit_length() + 7) // 8
                cli_sock.send(bytes([size_len]))

                # Send the actual pixels length
                size_bytes = size.to_bytes(size_len, 'big')
                # Encrypt with aes only this message (the most important message)
                cli_sock.send(size_bytes)

                # TODO: check with aes
                # raw = pad(size_len)
                # iv = Random.new().read(AES.block_size)
                # cipher = AES.new(key.encode(), AES.MODE_CBC, iv)
                # cli_sock.send(base64.b64encode(iv + cipher.encrypt(raw.encode())))

                # Send pixels
                cli_sock.sendall(pixels)

                # # Handle keyboard inputs
                # keyboard_data = cli_sock.recv(1024)
                # handle_keyboard_request(keyboard_data.decode())

                # # # Handle mouse events
                # mouse_data = cli_sock.recv(1024)
                # handle_mouse_requests(mouse_data.decode())
        except Exception as e:
            print(e)


def diffieH(sock):
    sock.send("dp".encode())
    g, n = sock.recv(1024).decode().split('|')
    g = int(g)
    n = int(n)

    while True:
        # exchange the mix of the private key and n
        ag = sock.recv(1024)
        if ag != b"":
            break
    ag = int(ag.decode())

    # Set "b" (second side private variable)
    b = random.randint(0, n)

    # Set the public parameter "bg"
    sock.send(str(pow(g, b) % n).encode())

    # Mix the private variable with the mix of the other side
    return str(pow(ag, b) % n)  # Key


def handle_identification(cli_sock):
    data = cli_sock.recv(1024)
    if data != b"empty":
        app = wx.App(0)
        Login(None, -1, 'Remote Control', cli_sock)
        app.MainLoop()
    else:
        app = wx.App(0)
        Register(None, -1, 'Remote Control', cli_sock)
        app.MainLoop()


def main(host="127.0.0.1", port=1234):
    # Setting up the client
    sock = socket()
    sock.connect((host, port))

    # handle_identification(sock)

    # Getting the private key for the encryptions
    # key = diffieH(sock)

    try:
        retreive_screenshot(sock)  # ,key
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()  # sys.argv[1],sys.argv[2]
