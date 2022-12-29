
# ALEKA ABEBE

## The Game
ALEKA ABEBE is an Ethiopian themed 8-bit side scrolling, infinite level platform game, 

#### Main Menu
On loading the game, you are met with the main menu.  The play button will lead you to an intro cutscene followed by the game, while settings opens the settings menu.  You can quit game from here, and the about button leads to this web page.
#### Gameplay
Gameplay is relatively simple, use the WASD keys to move your character and the space bar to attack. When all the characters in the level have been defeated a message will appear that the level is complete, and press e to move to the next level.

The game can be paused by pressing the escape key at any time, which will load the pause menu. From here you can continue gameplay, quit game or quit to main menu.

The score is calculated based on number of health points taken by the character, vs number of health points the character takes. Each point the character takes equates to 1 point, and every 5 health points the character loses loses them 1 point.

#### Settings

In the settings menu you can change the key bindings to your preferred set.  To do this simply press the change button next to the corresponding action.  The action text will highlight in red.  Press the key on your keyboard that you would like to set the action to and the binding will be updated.  To change the background track, simply press the music button at the bottom and it will iterate through the available tracks.  To return to the default settings, press the reset button.
## Installation
To play ALEKA ABEBE you need the following installations on your system

Python 3, with version >= 3.8.5
PyGame version >= 2.0.0


#### Windows
Download python from the downloads page of the python website.

To install pygame (required to play the game), run `pip install pygame` from the command line. This will install the latest version of pygame.

If you already have an older version of pygame installed on your computer you will need to upgrade it to play.  To do this, run `pip install pygame==2.0.0`

The game can then be run by running White Kninght.py from the projects root directory, or by double clicking the White Kninght.py icon from within Windows explorer.

#### Linux
White Kninght has been tested on Ubuntu 20.04, but should run on other flavours of linux.

Ensure python3 is installed on your system, if it is not installed, run `sudo apt-get install python3`, or use your favourite package manager.

To install pygame, run `pip3 install pygame`

To give execute permissions, make sure to run `chmod +x White Kninght.py`

Run `python3 ALEKA-ABEBE.py` from the projects root directory.
#### Mac OS
We have been unable to test this project on Mac OS, however as it has been tested on various flavours of Linux we see no reason why it should fail on a mac.
Ensure python3 and pygame 2 are installed.
