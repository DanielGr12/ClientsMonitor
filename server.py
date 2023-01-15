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

keyboard = Controller()
HASH_PEPPER = "Aa5!gGpR"
BS = 16


width, height = pyautogui.size()
maxWidth, maxHeight = pyautogui.size()
width -= 1
height -= 30
mouseAndKeyboard = False
clients = 0
lock = threading.Lock()
images = {}
width, height = pyautogui.size()
width -= 1
height -= 30

InitBoard = True

mainScreen = None
clock = None


def pad(s):
    s = str(s)
    return s + (BS - len(s) % BS) * chr(BS - len(s) % BS)


def unpad(s):
    s = str(s)
    return s[:-ord(s[len(s)-1:])]


def recvall(cli_sock, length):
    """ Retreive all pixels. """

    buf = b''
    while len(buf) < length:
        data = cli_sock.recv(length - len(buf))
        if not data:
            return data
        buf += data
    return buf


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


def drawScreens():
    newImages = {}
    x, y = 0, 0
    coordinates = []
    for item in images:
        width, height = calculate_dimensions()
        newImage = pygame.transform.scale(
            images[item], (960, 540))
        newImages[item] = newImage
        coordinates.append((x, y))
        if (x+width >= maxWidth):
            y += height
            x = 0
        else:
            x += width

    for coordinate in coordinates:
        mainScreen.blit(newImage, (coordinate[0], coordinate[1]))

    pygame.draw.line(mainScreen, (255, 255, 255), [
        0, maxHeight//2], [maxWidth, maxHeight//2], 2)
    pygame.draw.line(mainScreen, (255, 255, 255), [
        maxWidth//2, 0], [maxWidth//2, maxHeight], 2)
    pygame.display.flip()

    # y += height
def refresh_clients():
    # Drawing a black Rectangle
    pygame.draw.rect(mainScreen, (0,0,0), pygame.Rect(0, 0, maxWidth, maxHeight))
    pygame.display.flip()

def screen(sock, addr):  # , key
    global keyboard_action, mouse_action, images, mainScreen, clock, InitBoard,clients
    width, height = pyautogui.size()
    width -= 1
    height -= 30
    if (InitBoard):
        pygame.init()
        mainScreen = pygame.display.set_mode(
            (width, height))  # , pygame.FULLSCREEN
        clock = pygame.time.Clock()
        InitBoard = False

    # pygame.FULLSCREEN works but cant check with it on the same computer

    watching = True

    # Add mouse listeners
    if (mouseAndKeyboard):
        init_mouse()

    try:
        while watching:

            for event in pygame.event.get():
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
            try:
                # Retreive the size of the pixels length, the pixels length and pixels
                size_len = int.from_bytes(sock.recv(1), byteorder='big')

                # TODO: check with aes
                # data = sock.recv(size_len)
                # enc = base64.b64decode(data)
                # iv = enc[:16]
                # if iv != b"":
                #     cipher = AES.new(key.encode(), AES.MODE_CBC, iv )
                #     size = int.from_bytes(unpad(cipher.decrypt( enc[16:] )), byteorder='big') # Decrypt with aes or rsa only this message

                size = int.from_bytes(sock.recv(size_len), byteorder='big')
                pixels = decompress(recvall(sock, size))

                if (mouseAndKeyboard):
                    # Send keyboard input if there is one
                    sock.send(f"key~{keyboard_action}".encode())

                    # WORKS!
                    if mouse_action != "nothing":
                        sock.send(
                            f"mouse~{mouse.get_position()}~{mouse_action}".encode())
                    else:
                        sock.send("nothing".encode())

                # Create the Surface from raw pixels
                # height, width = 540, 960  #
                img = pygame.image.fromstring(
                    pixels, (width, height), 'RGB')  #

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

                drawScreens()
                pygame.display.flip()
                clock.tick(60)
                keyboard_action = "nothing"
                mouse_action = "nothing"
            except Exception as e:
                print(f"Error occurred, closing program.({e})")
                break

    finally:
        del images[addr]
        refresh_clients()
        lock.acquire()
        clients-=1
        lock.release()
        if(clients == 0):
            pygame.quit()
            InitBoard = True
        sock.close()


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


def handle_client(cli_sock, addr):  # , scrn, clock
    global clients
    print(f'Client connected IP: {addr}')
    lock.acquire()
    clients += 1
    lock.release()
    # handle_identification(cli_sock)

    # Getting the private key for the encryptions
    # key = diffieH(cli_sock)

    screen(cli_sock, addr)  # ,key, scrn, clock


def diffieH(sock):
    n = 3259
    g = 7
    sock.recv(1024)

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
    return str(pow(bg, a) % n)  # Key


def handle_identification(cli_sock):
    empty = False
    credentials = ""
    try:
        f = open("Project\database.txt", "r+")
    except:
        f = open("database.txt", "r+")
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
                hashed_pass = hashlib.sha256(
                    (HASH_PEPPER + salt + password).encode()).hexdigest()
                if (hashed_pass == credentials[1]):
                    cli_sock.send("correct".encode())
                    cont = False
    else:
        salt = gen_salt()
        hashed_pass = hashlib.sha256(
            (HASH_PEPPER + salt + password).encode()).hexdigest()
        to_write = f"{username}~{hashed_pass}~{salt}"
        f.write(to_write)
    f.close()


def gen_salt():  # create a unique salt to the passowrd
    salt = ""
    for i in range(10):
        char = random.randint(33, 126)
        salt += chr(char)
    return salt


def main(host="0.0.0.0", port=1234):
    threads = []
    # Setting up the server
    sock = socket()
    sock.bind((host, port))
    sock.listen(5)
    print('Server started.')
    # initPygame()
    while True:
        print('Main thread: before accepting ...')
        cli_sock, addr = sock.accept()

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


if __name__ == '__main__':
    main()  # sys.argv[1],sys.argv[2]
