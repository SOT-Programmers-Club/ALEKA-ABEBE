### Library Imports
import os
import webbrowser
import json
import pygame

from screens.game import pyfighterGame
from screens.settings import SettingsMenu
from classes.generalfunctions import quitGame
from classes.menu import Menu
from classes.menu import Button
from classes.text import Text

### Important Game Variables from JSON
with open('json/config.JSON') as config_file:
    config = json.load(config_file)

# Colour tuples and font sizesd 
colour = config['colour']
font_size = config['font_size']

# Important screen variables
screen_width = config['screen_dims'][0]
screen_height = config['screen_dims'][1]
max_fps = config['max_fps']
game_name = config['game_name']

### Setting up Screen and clock
menu_screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption(game_name)
clock = pygame.time.Clock()

### Setting Icon
logo_image = pygame.image.load(config['logo_location'])
pygame.display.set_icon(logo_image)

menu_background = config['start_menu_background']
menu_background_path = config['menu_music']

### Setting up Menu
# Menu Functions - These functions are passed into each menu button
def playGame():
    pyfighterGame()
    playMusic(menu_background_path)

def playMusic(music_path):
    ### Setting up game music
    # - Music code inspired by code here:
    #   https://riptutorial.com/pygame/example/24563/example-to-add-musi
    #   c-in-pygame
    # - Found detail on setting volume on pygame docs
    pygame.mixer.init()
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.play(-1)
    
def loadAbout():
    webbrowser.open('https://www.White Kninght.xyz/',
                            new=2)

def runSettings():
    return 'settings'

# String names
menu_title = game_name
play_text = 'Play'
about_text = 'About'
settings_text = 'Settings'
quit_text = 'Quit'

# Title position
title_x = screen_width // 2
title_y = screen_height // 9

# Calculating (x,y) coords of buttons
width_unit = screen_width // 6
height_unit = screen_height // 2

major_button_dims = (192, 64)

offset = 20

about_position = (screen_width - 64 - offset, 32 + offset)

# Creating pygame string objects
title_obj = Text(menu_screen, (title_x, title_y),
                        font_size['title'], menu_title, 'Seagreen')

play_button = Button(menu_screen, play_text, 
                    (1 * width_unit, height_unit), playGame, 35, major_button_dims)

settings_button = Button(menu_screen, settings_text,(3 * width_unit, height_unit), runSettings, 30, major_button_dims)

about_button = Button(menu_screen, about_text, 
                    about_position, loadAbout, 30)

quit_button = Button(menu_screen, quit_text, 
                    (5 * width_unit, height_unit), quitGame, 35, major_button_dims)


# Initialising StartMenu class
start_menu = Menu(menu_screen, title_obj, menu_background, play_button, 
                                                settings_button, about_button, quit_button)

# Start Music
playMusic(menu_background_path)

# Found on pygame docs
# https://www.pygame.org/docs/ref/cursors.html
# Believe it makes the cursor look nicer in the game
pygame.mouse.set_cursor(*pygame.cursors.tri_left)

### Main Game Loop
while start_menu.playing:
    # Limit frame rate
    clock.tick(max_fps)

    # Get/action events
    for event in pygame.event.get():
        # Send each event to the start menu
        button_out = start_menu.do(event)
        if button_out == 'settings':
            SettingsMenu(menu_screen, max_fps)
        
    # Refresh screen
    menu_screen.fill(colour['black'])

    ### Code to re-display items on screen will go here
    start_menu.display()

    # Display everything on screen
    pygame.display.flip()

quitGame()


