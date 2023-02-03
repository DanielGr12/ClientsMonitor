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
import tcp_by_size
import time
import keyboard
# from pynput.keyboard import Key, Controller
import pynput


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
frameWidth, frameHeight = pyautogui.size()
frameWidth -= 1
frameHeight -= 30
rect = {'top': 0, 'left': 0, 'width': frameWidth, 'height': frameHeight}


keyboard_action = "nothing"
mouse_action = "nothing"

mouseAndKeyboard = False
sleepTime = 0
lastSleepTime = 0
keysListen = False
BS = 16
# keyboard = Controller()

keyboard_listener = pynput.keyboard.Listener(suppress=True)
mouse_listener = pynput.mouse.Listener(suppress=True)


def pad(s): return s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
def unpad(s): return s[:-ord(s[len(s)-1:])]


def handle_server_event(evt, sock):
    global sleepTime, lastSleepTime, frameHeight, frameWidth, rect, keysListen, keyboard_listener, mouse_listener
    # Nothing
    if (evt == "~"):
        return
    elif (evt == "stop"):
        # pass
        # wait until event
        tcp_by_size.recv_by_size(sock)
    # elif (evt == "stop"):
    #     # wait until event
    #     tcp_by_size.recv_by_size(sock)
    elif (evt == "control"):
        lastSleepTime = sleepTime
        sleepTime = 0
        frameHeight += 30
        frameWidth += 1
        rect = {'top': 0, 'left': 0, 'width': frameWidth, 'height': frameHeight}

        # Recieve keys events
        keysListen = True
        # TODO: when returning to the manager window disable the inputs again if they were disabled
        if (keyboard_listener.is_alive() == False):
            keyboard_listener.start()
        # time.sleep(1)
        # TODO: activate mouse and keyboard
    # End control
    elif (evt == "eControl"):
        sleepTime = lastSleepTime
        frameHeight -= 30
        frameWidth -= 1
        rect = {'top': 0, 'left': 0, 'width': frameWidth, 'height': frameHeight}
        keysListen = False
        # time.sleep(1)
    # disable mouse and keyboard
    elif (evt == "disable_input"):
        # mouse_listener = pynput.mouse.Listener(suppress=True)
        # mouse_listener.start()
        if (keyboard_listener.is_alive() == False):
            keyboard_listener.start()
    elif (evt == "enable_input"):
        if (keyboard_listener.is_alive()):
            keyboard_listener.stop()
            keyboard_listener = pynput.keyboard.Listener(suppress=True)


def handle_keyboard_request(data):
    parts = data.split("~")
    if (parts[0] != "_" and parts[0] != ""):
        # l_alt = 1073742050,l_ctrl = 1073742048,r_alt = 1073742054,r_ctrl = 1073742052
        if (parts[0] == "1073742050" or parts[0] == "1073742054"):
            key = "alt"
        elif (parts[0] == "1073742048" or parts[0] == "1073742052"):
            key = "ctrl"
        else:
            key = chr(int(parts[0]))

        print(f"got - {key}")
        keyboard.send(key)
        # keyboard.press(key)
        # keyboard.release(key)


def retreive_screenshot(cli_sock):  # ,key
    global rect
    with mss() as sct:
        # The region to capture
        try:
            while 'recording':
                # Capture the screen
                img = sct.grab(rect)
                # Tweak the compression level here (0-9)
                pixels = compress(img.rgb, 6)

                tcp_by_size.send_with_size(cli_sock, pixels)
                print("sent")
                server_event = tcp_by_size.recv_by_size(cli_sock).decode()
                handle_server_event(server_event, cli_sock)
                time.sleep(sleepTime)
                # TODO: check with aes
                # raw = pad(size_len)
                # iv = Random.new().read(AES.block_size)
                # cipher = AES.new(key.encode(), AES.MODE_CBC, iv)
                # cli_sock.send(base64.b64encode(iv + cipher.encrypt(raw.encode())))

                # Handle keyboard inputs
                if (keysListen):
                    keyboard_data = tcp_by_size.recv_by_size(cli_sock)
                    handle_keyboard_request(keyboard_data.decode())

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
    global sleepTime
    # Setting up the client
    sock = socket()
    sock.connect((host, port))
    # handle_identification(sock)

    # Getting the private key for the encryptions
    # key = diffieH(sock)

    try:
        # calculate the sleep between each frame
        fps = int(sock.recv(1024).decode())
        if (fps == 0):
            sleep_time = 0
        else:
            sleep_time = 1/fps

        sleepTime = sleep_time
        retreive_screenshot(sock)  # ,key
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()  # sys.argv[1],sys.argv[2]
