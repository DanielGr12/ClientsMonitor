from os import system
from socket import socket
import threading
from zlib import compress, decompress
from mss import mss
from pynput.keyboard import Key, Controller
import mouse
import random
import hashlib
# from Crypto.Cipher import AES
# from Crypto import Random
import base64
import pyautogui
import sys
import pygame
import tcp_by_size
from datetime import date, datetime
import time
import pynput
from argon2 import PasswordHasher, Type
import Classes
import wx
import ctypes
from Crypto.Cipher import AES
from zipfile import ZipFile
import tkinter as tk

keyboard = Controller()
HASH_PEPPER = "Aa5!gGpR"
BS = 16

WHITE = (255, 255, 255)
maxWidth, maxHeight = pyautogui.size()
mouseAndKeyboard = False
clients = []
lock = threading.Lock()
images = {}
clientsKeys = {}

width, height = pyautogui.size()
# Reduce the width and height because if they are on the max the windows tab will not appear
width -= 1
height -= 30


buttons = []  # ["control", "remove", "image", "disable_input"]
InitBoard = True
srv_event = "~"
mainScreen = None
clock = None
controlMode = False
tab = None


client_fps = 0
tab_dimensions = None

clients_sockets = {}

keysDisabled = False
keyboard_action = "_"
mouse_action = "_"

windowWidth, windowHeight = pyautogui.size()
windowWidth -= 1
windowHeight -= 30
frameWidth = windowWidth//2
frameHeight = windowHeight//2
key = ""
removeClient = ""
app = wx.App(0)
mainThreadEvent = ""
RightArrow = pygame.image.load("RightArrow.png")
RightArrow = pygame.transform.scale(RightArrow, (windowWidth//100, 30))


def pad(s):
    s = str(s)
    return s + (BS - len(s) % BS) * chr(BS - len(s) % BS)


def unpad(s):
    s = str(s)
    return s[:-ord(s[len(s)-1:])]


def change_val(value):
    global mouse_action
    mouse_action = value


def init_mouse():
    mouse.on_click(lambda: change_val("left"))
    mouse.on_double_click(lambda: change_val("double"))
    mouse.on_middle_click(lambda: change_val("middle"))
    mouse.on_right_click(lambda: change_val("right"))


def open_menu():
    pass


def calculate_dimensions():
    # screen = pygame.display.set_mode()
    width, height = mainScreen.get_size()

    return width//2, height//2,


def DrawArrows(direction, xPos, yPos):
    if ("L" in direction):
        # Draw Left
        LeftArrow = pygame.transform.rotate(RightArrow, 180)
        rect = pygame.Rect(xPos+1, yPos+(frameHeight//2-50),
                           frameWidth//13, 50)
        pygame.draw.rect(mainScreen, WHITE, rect)
        mainScreen.blit(LeftArrow, (xPos+20, yPos+(frameHeight//2-50)+10))
    if ("R" in direction):
        rect = pygame.Rect(xPos+(frameWidth-frameWidth//13)+1,
                           yPos+(frameHeight//2-50), frameWidth//13, 50)
        pygame.draw.rect(mainScreen, WHITE, rect)
        mainScreen.blit(
            RightArrow, (xPos+(frameWidth-frameWidth//13)+20, yPos+(frameHeight//2-50)+10))


def CheckArrowsClicks(direction, clickPos, startX, startY, num):
    global srv_event, clients
    if ("L" in direction):
        if (clickPos[0] > startX and clickPos[0] < startX+frameWidth//13):
            if (clickPos[1] > startY+(frameHeight//2-50) and clickPos[1] < startY+(frameHeight//2-50)+50):
                client = clients[num].split("~")
                if (int(client[2])-1 >= 0):
                    client[2] = str(int(client[2])-1)
                    clients[num] = f"{client[0]}~{client[1]}~{client[2]}"
                    srv_event = "leftMon"
                    print("left")
    if ("R" in direction):
        if (clickPos[0] > startX+(frameWidth-frameWidth//13)+1 and clickPos[0] < startX+frameWidth):
            if (clickPos[1] > startY+(frameHeight//2-50) and clickPos[1] < startY+(frameHeight//2-50)+50):
                client = clients[num].split("~")
                if (int(client[2]) < int(client[1])):
                    client[2] = str(int(client[2])+1)
                    clients[num] = f"{client[0]}~{client[1]}~{client[2]}"
                    srv_event = "rightMon"
                    print("Right")


def HandleMonitorsButtons(num):
    # Check if the client has more than one monitor
    client_data = clients[num-1].split("~")
    if (int(client_data[1]) >= 1):  # >= 1 is two monitors(0,1)
        # Check on which monitor the images are from

        # Check if the active monitor is on the first
        if (int(client_data[2]) == 0):
            # show only right arrow
            direction = "R"
        elif (int(client_data[2]) == int(client_data[1])):
            direction = "L"
        else:
            direction = "RL"

        if (num == 1):
            DrawArrows(direction, 0, 0)
        elif (num == 2):
            DrawArrows(direction, windowWidth, 0)
        elif (num == 3):
            DrawArrows(direction, 0, windowHeight)
        elif (num == 4):
            DrawArrows(direction, windowWidth, windowHeight)


def getClientNumber(drawOptions=True):
    x, y = pygame.mouse.get_pos()
    num = 5
    if (x < maxWidth//2 and y < maxHeight//2):
        xPos, yPos = 0, 0
        num = 1
    elif (x > maxWidth//2 and y < maxHeight//2 and num < len(clients)):
        xPos, yPos = maxWidth//2, 0
        num = 2
    elif (x < maxWidth//2 and y > maxHeight//2 and num < len(clients)):
        xPos, yPos = 0, maxHeight//2
        num = 3
    elif (x > maxWidth//2 and y > maxHeight//2 and num < len(clients)):
        xPos, yPos = maxWidth//2, maxHeight//2
        num = 4
    if (num == 5 or num > len(clients)):
        return 0
    if (drawOptions == True):
        # Check if the user has more than one monitor and show the button of changing to the other monitors
        HandleMonitorsButtons(num)

        if (Classes.currentManager.privileges > 1):
            mainScreen.blit(tab, (xPos, yPos))

            # draw the active dot of the keyboard and mouse (if the privileges level is higher than 2)
            if (Classes.currentManager.privileges > 2):
                offset = 0
                if (Classes.currentManager.privileges == 4):
                    offset = frameWidth//len(buttons)+25
                if (keysDisabled == True):
                    pygame.draw.circle(mainScreen, (255, 0, 0),
                                       (xPos+frameWidth-17-offset, yPos+20), 8, 9)
                else:
                    pygame.draw.circle(mainScreen, (0, 255, 0),
                                       (xPos+frameWidth-17-offset, yPos+20), 8, 9)
    pygame.display.update()
    return num
    # ip = clients[num-1]
    # return ip


def drawScreens():
    newImages = {}
    x, y = 0, 0
    coordinates = {}
    # Scale down the size of each image to the part of the screen it needs to take,
    # save the coordinates of each client's image
    for item in images:
        width, height = calculate_dimensions()
        newImage = pygame.transform.scale(
            images[item], (960, 540))
        newImages[item] = newImage
        coordinates[item] = (x, y)
        if (x+width >= maxWidth):
            y += height
            x = 0
        else:
            x += width

    # Blit each image to the screen with the correct coordinates
    for item in newImages:
        mainScreen.blit(newImages[item],
                        (coordinates[item][0], coordinates[item][1]))

    num = getClientNumber()
    if (Classes.currentManager.privileges > 1):

        font = pygame.font.Font('freesansbold.ttf', 32)

        # create a text surface object,
        # on which text is drawn on it.
        # text = font.render(str(clients[num-1]),
        #                    True, (255, 255, 255), (0, 0, 128))
        # textRect = text.get_rect()
        # textRect.center = (maxWidth // 2, maxHeight // 2)
        # mainScreen.blit(text, textRect)

    pygame.draw.line(mainScreen, (255, 255, 255), [
        0, maxHeight//2], [maxWidth, maxHeight//2], 2)
    pygame.draw.line(mainScreen, (255, 255, 255), [
        maxWidth//2, 0], [maxWidth//2, maxHeight], 2)

    # y += height


def refresh_clients():
    # Drawing a black Rectangle
    pygame.draw.rect(mainScreen, (0, 0, 0),
                     pygame.Rect(0, 0, maxWidth, maxHeight))
    pygame.display.flip()


# This function gets an action and does the event it should
def do_button_action(evt, addr):
    global srv_event, mainScreen, controlMode, windowWidth, windowHeight, keysDisabled, removeClient, mainThreadEvent
    # this makes the user control one of the client's computer
    if (evt == "control"):
        # TODO: send all the other clients command that will stop them from sending pictures
        srv_event = "control"
        # pygame.quit()
        # pygame.init()
        mainScreen = pygame.display.set_mode(
            (maxWidth, maxHeight), pygame.FULLSCREEN)  # , pygame.FULLSCREEN
        controlMode = True
        windowHeight += 30
        windowWidth += 1
        broadcast_all(addr)

    elif (evt == "image"):
        today = date.today()
        now = datetime.now()
        current_time = now.strftime("%H.%M.%S")
        pygame.image.save(images[addr], f"{addr}~{today}~{current_time}.jpg")
    elif (evt == "disable_input"):
        if (keysDisabled == True):
            srv_event = "enable_input"
        else:
            srv_event = "disable_input"
        # turn the disable flag off or on
        keysDisabled = not keysDisabled
    elif (evt == "remove"):
        deleteClient(addr)
    elif (evt == "getFile"):
        mainThreadEvent = "file"
        # Classes.FileDialog(None, 0, 'File Dialog')
        # app.MainLoop()


def handleClicks(pos, addr):
    # get the client that click was on(to check the tab position)
    client = getClientNumber(False)
    client -= 1
    # Get the client's screen position
    clientScreenX = client % 2*(maxWidth//2)
    if (client > 1):
        clientScreenY = maxHeight//2
    else:
        clientScreenY = 0

    # Check on which button the user clicked with width of every button
    # the buttons variable contains the amout of buttons that are on the tab

    if (pos[0] > clientScreenX and pos[0] < clientScreenX+maxWidth//2):
        # Check if the user on one of the buttons(if there are any):

        client_data = clients[client].split("~")
        # check if the client has more than one monitor
        if (int(client_data[1]) >= 1):
            # Check on which monitor the images are from

            # Check if the active monitor is on the first
            if (int(client_data[2]) == 0):
                # show only right arrow
                direction = "R"
            elif (int(client_data[2]) == int(client_data[1])):
                direction = "L"
            else:
                direction = "RL"

            CheckArrowsClicks(direction, pos, clientScreenX,
                              clientScreenY, client)

        if (Classes.currentManager.privileges > 1):
            windowSize = maxWidth // 2
            xPos = pos[0]
            portion = windowSize//len(buttons)
            # Check if the user clicked on the tab
            if (pos[1] > clientScreenY and pos[1] < clientScreenY+maxHeight//2):
                if (pos[1] < tab_dimensions[1]+clientScreenY):
                    # Check on which button the user clicked
                    for button in buttons:
                        if (xPos < clientScreenX+portion):
                            do_button_action(button, addr)
                            break
                        clientScreenX += portion


# broadcast all the clients except the address of the client that is passed as a parameter
def broadcast_all(addr):
    # determine whether to send stop sending images or to start again
    if (controlMode == True):
        # broadcast all clients to stop streaming
        command = "stop"
    else:
        command = "stream"
        tcp_by_size.send_with_size(clients_sockets[addr], "eControl")

    for item in clients_sockets:
        if (item != addr):
            tcp_by_size.send_with_size(clients_sockets[item], command)


def stop_control(addr):
    global controlMode, InitBoard, mainScreen, windowWidth, windowHeight, controlMode
    controlMode = False
    InitBoard = True
    broadcast_all(addr)
    init_board()
    # init the display twice because there is a bug in pygame that doesn't resize when i return to resizeable
    mainScreen = pygame.display.set_mode(
        (width, height), pygame.RESIZABLE)
    refresh_clients()
    controlMode = False
    windowHeight -= 30
    windowWidth -= 1
    # time.sleep(1)
    # pygame.quit()
    # init_board()


def init_board():
    global InitBoard, tab, clock, mainScreen, tab_dimensions, buttons
    if (InitBoard):
        pygame.init()
        mainScreen = pygame.display.set_mode(
            (width, height), pygame.RESIZABLE)
        pygame.display.update()
        if (tab == None):
            clock = pygame.time.Clock()
            if (Classes.currentManager.privileges == 2):
                tab = pygame.image.load("controls2.png").convert()
                buttons = ["image"]
            elif (Classes.currentManager.privileges == 3):
                tab = pygame.image.load("controls3.png").convert()
                buttons = ["control", "remove", "image", "disable_input"]
            elif (Classes.currentManager.privileges == 4):
                tab = pygame.image.load("controls4.png").convert()
                buttons = ["control", "remove",
                           "image", "disable_input", "getFile"]
            if (tab != None):
                tab_dimensions = (maxWidth//2, maxHeight//18)
                tab = pygame.transform.scale(tab, tab_dimensions)
        InitBoard = False


def draw_user_screen(addr):
    mainScreen.blit(images[addr], (0, 0))
    pygame.display.flip()


def UpdateScreen(addr):
    if (controlMode == True):
        draw_user_screen(addr)
    else:
        drawScreens()

    pygame.display.flip()


def close_popup(popup):
    popup.destroy()


def show_popup():
    popup = tk.Tk()
    popup.title("Error")
    popup.geometry("200x100")
    popup_label = tk.Label(popup, text="Error while authenticating the file")
    popup_label.pack(pady=20)
    popup.after(3000, lambda: close_popup(popup))
    popup.mainloop()


def deleteClient(addr):
    global clients, images, clients_sockets, InitBoard
    del images[addr]
    # check 413
    clients_sockets[addr].close()
    del clients_sockets[addr]
    refresh_clients()
    for c in clients:
        parts = c.split("~")
        if (parts[0] == addr):
            lock.acquire()
            clients.remove(c)
            lock.release()
    if (len(clients) == 0):
        pygame.quit()
        InitBoard = True
    # sock.close()

# Create the named file and write the data, Check if the digital signature is correct


def splitData(data):
    parts = []
    bts = [i.to_bytes(1, sys.byteorder) for i in data]
    string = b""
    for letter in bts:
        if (letter == b"|"):
            parts.append(string)
            string = b""
        else:
            string += letter
    parts.append(string)
    return parts


def HandleFileSaving(fileData):
    parts = splitData(fileData)
    # print(fileData[7:])
    # parts = fileData[7:].decode().split("~")
    data = parts[1]
    tag = parts[3]
    nonce = parts[2]
    # hmac Here:
    print(f"cipher:{data}\ntag:{parts[3]}\nNonce:{parts[2]}")
    cipher = AES.new(key.encode(), AES.MODE_EAX, nonce)

    try:
        data = cipher.decrypt_and_verify(data, tag)
    except:
        return False

    checkHash = hashlib.sha256()
    checkHash.update(data+key.encode())

    data = data.decode()

    if (checkHash.digest() == parts[4]):
        # Save file:
        with open(Classes.copiedFileName, "w") as f:
            f.write(data)
    return True


def screen(sock, addr):  # , key
    global keyboard_action, mouse_action, images, mainScreen, clock, clients, srv_event, removeClient

    init_board()

    watching = True

    # Add mouse listeners
    if (mouseAndKeyboard):
        init_mouse()

    try:
        while watching:

            for event in pygame.event.get():
                if (controlMode == True):
                    keys = pygame.key.get_pressed()
                    # print(keys)

                    if event.type == pygame.KEYDOWN:
                        # Check if the user pressed on alt+1+ctrl
                        if (keys[pygame.K_LALT] or keys[pygame.K_RALT]) and keys[pygame.K_1] and (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]):
                            stop_control(addr)
                        else:
                            keyboard_action = str(event.key)
                        # print(str(event.key))

                else:
                    if event.type == pygame.MOUSEBUTTONUP:
                        pos = pygame.mouse.get_pos()
                        handleClicks(pos, addr)

                if (mouseAndKeyboard):
                    keys = pygame.key.get_pressed()
                    if event.type == pygame.QUIT:
                        watching = False
                        mouse.unhook_all()
                        break
                    if event.type == pygame.KEYDOWN:
                        keyboard_action = str(event.key)
                        if event.key == pygame.K_ESCAPE:
                            watching = False
                            mouse.unhook_all()
                            break
                        if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                            keyboard_action = "nothing"
                        if event.key == pygame.K_LALT or event.key == pygame.K_RALT:
                            open_menu()
                    if event.type == pygame.MOUSEBUTTONUP:
                        pos = pygame.mouse.get_pos()

            # This try and except makes sure that the program will not crash when changing dimensions
            # (when changing to fullscreen the dimensions change but the client has already sent an image with a different dimensions)
            try:
                pixels = tcp_by_size.recv_by_size(sock)
                tcp_by_size.send_with_size(sock, srv_event)
                if ("getFile" in srv_event):
                    fileData = tcp_by_size.recv_by_size(sock)

                    if (HandleFileSaving(fileData) == False):
                        show_popup()
                # if (srv_event == "control"):
                srv_event = "~"
                # TODO: check with aes
                # data = sock.recv(size_len)
                # enc = base64.b64decode(data)
                # iv = enc[:16]
                # if iv != b"":
                #     cipher = AES.new(key.encode(), AES.MODE_CBC, iv )
                #     size = int.from_bytes(unpad(cipher.decrypt( enc[16:] )), byteorder='big') # Decrypt with aes or rsa only this message

                pixels = decompress(pixels)
                if (controlMode == True):
                    tcp_by_size.send_with_size(sock, f"{keyboard_action}")
                    keyboard_action = "_"

                if (mouseAndKeyboard):
                    # Send keyboard input if there is one
                    sock.send(f"keyboard~{keyboard_action}".encode())

                    # WORKS!
                    if mouse_action != "nothing":
                        sock.send(
                            f"mouse~{mouse.get_position()}~{mouse_action}".encode())
                    else:
                        sock.send("nothing".encode())

                # Create the Surface from raw pixels
                # height, width = 540, 960  #
                try:
                    img = pygame.image.fromstring(
                        pixels, (windowWidth, windowHeight), 'RGB')  #

                    # Display the picture
                    # if (first):

                    # first = False
                    lock.acquire()

                    # images["bb"] = img
                    # images["aa"] = img
                    # images["cc"] = img
                    # images["dd"] = img
                    print(addr)
                    images[addr] = img
                    lock.release()

                    UpdateScreen(addr)

                    # if (removeClient != ""):
                    #     deleteClient(removeClient)
                    #     removeClient = ""

                    pygame.display.flip()
                    clock.tick(60)

                    mouse_action = "nothing"
                except Exception as dimensionsE:
                    print(f"error with dimensions - {dimensionsE}")

            except Exception as e:
                print(f"Error occurred, closing program.({e})")
                break

    finally:
        if (addr in images):
            deleteClient(addr)


def handle_mouse_requests(data):
    if data != "nothing":
        parts = data.split("~")
        positions = parts[1].split(",")

        # Remove the parenthesis and spaces
        positions[0] = positions[0][1:]
        positions[1] = positions[1][1:-1]
        mouse.move(positions[0], positions[1])
        if parts[2] == "right":
            mouse.click('right')
        if parts[2] == "left":
            mouse.click('left')
        if parts[2] == "double":
            mouse.double_click('left')
        if parts[2] == "middle":
            mouse.click('middle')


def handle_keyboard_request(data):
    parts = data.split("~")
    if parts[1] != "nothing":
        key = chr(int(parts[1]))
        keyboard.press(key)
        keyboard.release(key)


def keyboard_listener(cli_sock):
    while True:
        data = cli_sock.recv(1024)
        if data != b"":
            handle_keyboard_request(data.decode())


def handle_client(cli_sock, addr):
    global clients, key
    print(f'Client connected IP: {addr}')

    # send the client the fps rate
    cli_sock.send(str(client_fps).encode())

    # handle_identification(cli_sock)
    # Get the user's amount of monitors
    monitors = tcp_by_size.recv_by_size(cli_sock)

    # Getting the private key for the encryptions
    key = diffieH(cli_sock)
    clientsKeys[addr[0]] = key

    lock.acquire()
    clients.append(f"{addr[0]}~{str(int(monitors.decode())-1)}~0")
    lock.release()

    screen(cli_sock, addr[0])


def diffieH(sock):
    n = 3259
    g = 7
    start = sock.recv(1024)
    if (start == b"dp"):
        sock.send(f"{str(g)}|{str(n)}".encode())

        # Set "a" (first side private variable)
        a = random.randint(0, n)

        # Send "ag" to the other side
        sock.send(str(pow(g, a) % n).encode())

        while True:
            # exchange the mix of the private key and n
            bg = sock.recv(1024).decode()
            if bg != b"":
                break

        # Mix the private variable with the mix of the other side
        bg = int(bg)
        k = str(pow(bg, a) % n)  # Key
        padded_key = k
        round = len(k)
        index = 0
        while (len(padded_key) < 16):
            if (index == round):
                index = 0
            padded_key += k[index]
            index += 1
        return padded_key

# This function will decrypt the encrypted Privilege level


def CalculatePrivileges(privilege):
    return privilege


def SignIn():
    # password P: the password (or message) to be hashed
    # salt S: random-generated salt(16 bytes recommended for password hashing)
    # iterations t: number of iterations to perform
    # memorySizeKB m: amount of memory ( in kilobytes) to use
    # parallelism p: degree of parallelism(i.e. number of threads)
    # outputKeyLength T: desired number of returned bytes
    # ph = PasswordHasher(
    #     memory_cost=65536,
    #     time_cost=16,
    #     parallelism=4,
    #     hash_len=32,
    #     type=Type.ID
    # )
    # salt = gen_salt()

    # app = wx.App(0)
    # Classes.SignUp(None, -1, 'Remote Control')
    # app.MainLoop()
    # Classes.FileDialog(None, -1, 'Remote Control')
    # app.MainLoop()
    Classes.currentManager = Classes.Manager("a", 1)

    return True  # Classes.currentManager != None


def handle_identification(cli_sock):

    empty = False
    credentials = ""
    try:
        f = open("Users.txt", "r+")
    except:
        f = open("Users.txt", "w+")
    credentials = f.read()
    if (credentials == ""):
        cli_sock.send("empty".encode())
        empty = True
    else:
        cli_sock.send("not empty".encode())
    data = cli_sock.recv(1024)
    parts = data.decode().split("~")
    username = parts[0]
    password = parts[1]
    if empty is False:
        credentials = credentials.split("~")
        salt = credentials[2]
        # passwordHash = ph.hash((HASH_PEPPER + salt + password))
        hashed_pass = hashlib.sha256(
            (HASH_PEPPER + salt + password).encode()).hexdigest()
        if (hashed_pass == credentials[1]):
            cli_sock.send("correct".encode())
        else:
            cont = True
            while cont:
                cli_sock.send("wrong".encode())
                data = cli_sock.recv(1024)
                parts = data.decode().split("~")
                password = parts[1]
                # passwordHash = ph.hash((HASH_PEPPER + salt + password))
                # print(passwordHash)
                hashed_pass = hashlib.sha256(
                    (HASH_PEPPER + salt + password).encode()).hexdigest()
                if (hashed_pass == credentials[1]):
                    cli_sock.send("correct".encode())
                    cont = False
    else:
        salt = gen_salt()

        hashed_pass = hashlib.sha256(
            (HASH_PEPPER + salt + password).encode()).hexdigest()
        print(hashed_pass)

        to_write = f"{username}~{hashed_pass}~{salt}"
        f.write(to_write)
    f.close()


def gen_salt():  # create a unique salt to the passowrd
    salt = ""
    for i in range(10):
        char = random.randint(33, 126)
        salt += chr(char)
    return salt


def SrvTh(host, port, threads):
    global clients_sockets

    # Setting up the server
    sock = socket()
    sock.bind((host, port))
    sock.listen(5)
    print('Server started.')
    # initPygame()
    while True:
        print('Main thread: before accepting ...')
        cli_sock, addr = sock.accept()
        clients_sockets[addr[0]] = cli_sock
        thread = threading.Thread(
            target=handle_client, args=(cli_sock, addr))  # ,scrn,clock
        threads.append(thread)
        thread.start()
        if len(threads) > 100000000:
            print('Main thread: going down for maintenance')
            break

    all_to_die = True
    print('Main thread: waiting to all clients to die')
    for t in threads:
        t.join()
    sock.close()
    print('Bye ..')


def handleMainThEvents():
    global srv_event, mainThreadEvent
    if (mainThreadEvent == "file"):

        # whnd = frame.GetHandle()
        # ctypes.windll.user32.ShowWindow(whnd, 5)
        # frame.Show()
        # frame = Classes.FileDialog(None, -1, 'Remote Control')
        # frame.Raise()
        # app.MainLoop()
        Classes.fileName = "E:\FinalProject\\todo.txt"
        Classes.copiedFileName = "dup.txt"
        srv_event = f"getFile~{Classes.fileName}"
        mainThreadEvent = ""


def main(host="0.0.0.0", port=1234):
    threads = []
    exit = False
    # Logging in to the user
    res = SignIn()
    if (res == True):
        srvThread = threading.Thread(
            target=SrvTh, args=(host, port, threads))
        threads.append(srvThread)
        srvThread.start()
        while (not exit):
            if (mainThreadEvent != ""):
                handleMainThEvents()


if __name__ == '__main__':
    print("aaa")
    main()  # sys.argv[1],sys.argv[2]
