# import the pygame module
import pygame
import pyautogui

# Define the background colour
# using RGB color coding.

width, height = pyautogui.size()
width -= 1
height -= 30
background_colour = (234, 212, 252)
pygame.init()
# Define the dimensions of
# screen object(width,height)
screen = pygame.display.set_mode(
    (width, height),pygame.RESIZABLE)  # , pygame.FULLSCREEN

clock = pygame.time.Clock()
#

# Set the caption of the screen
pygame.display.set_caption('Geeksforgeeks')

# Fill the background colour to the screen
screen.fill(background_colour)

# Update the display using flip
pygame.display.flip()

# Variable to keep our game loop running
running = True

# # game loop
while running:

    # for loop through the event queue
    for event in pygame.event.get():

        # Check for QUIT event
        if event.type == pygame.QUIT:
            running = False


    x, y = pygame.mouse.get_pos()
    # if(x == 0 and y == 0):
    print(f"{x},{y}")
    # pass
