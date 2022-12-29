''' Controller Class

The controller class.  This class controls the main game.

This file also contains the main game score and level outputs.

@author: All - Prototyped by Shaylen, finished collaboratively
'''

import pygame
import random
import json
from classes.map import Map
from classes.player import Player
from classes.npc import NPC
from classes.camera import Camera
from classes.background import Background
from classes.text import Text
from classes.weapon import WEAPON_TYPES
from screens.gameover import gameOver
from screens.pause import pauseScreen
from screens.intro import introScreen

# Possible enemies
ENEMIES = ['whitie1', 'whitie2']

# Player starting x value
PLAYER_X_VAL = 50

with open('json/background_music.JSON') as music_locations:
    MUSIC_LOCATIONS = json.load(music_locations)
    TRACKS = MUSIC_LOCATIONS['tracks']


class Controller():
    # X position that player starts level at
    player_x = PLAYER_X_VAL


    def __init__(self, game_display, game_screen, screen_dims, colour,
                                                            clock_delay):
        # Run game - used to exit game loop
        self.run = True

        # Load game settings
        with open('json/settings.JSON') as settings:
            self.settings = json.load(settings)

        # Add important game features to self
        self.game_display = game_display
        self.game_screen = game_screen
        self.screen_dims = screen_dims
        self.colour = colour
        self.clock_delay = clock_delay

        # Setup score and level displays
        self.score = Score(game_screen)
        self.level = Level(game_screen)

        # Setup key distances
        self.spawn_area = (2 * self.player_x, screen_dims[0])
        self.map_width = self.game_screen.get_width()
        self.mid_width = self.map_width // 2
        self.mid_height = self.game_screen.get_height() // 2

        self.weapon_types = list(WEAPON_TYPES.keys())

        # Setup level complete variables
        self.level_complete = False
        self.level_complete_text_1 = Text(self.game_screen,
                                        (self.mid_width, self.mid_height - 40),
                                        30,
                                        'Level Complete'
                                    )
        continue_string =  f'Press {self.settings["next_level"]} to continue'
        self.level_complete_text_2 = Text(self.game_screen,
                                        (self.mid_width, self.mid_height),
                                        30,
                                        continue_string
                                    )

        # Setup first level
        self.firstLevel()

        # Setup god mode capability - used for debugging
        self.god_mode = False
        self.cheats = 0

        # Play game music
        self.playMusic()

        self.projectiles = pygame.sprite.Group()


    def playMusic(self):

        ### Setting up game music
        # - Music code inspired by code here:
        #   https://riptutorial.com/pygame/example/24563/example-to-add-
        #   music-in-pygame
        track = TRACKS[self.settings['music']]
        if track == 'Mute':
            pygame.mixer.music.stop()
        else:        
            level_music = MUSIC_LOCATIONS[track]
            pygame.mixer.music.set_volume(level_music[1])
            pygame.mixer.music.load(level_music[0])
            pygame.mixer.music.play(-1)

    def setupCameraMap(self):
        '''
        Sets up camera and map for a given level
        '''
        self.camera = Camera(self.game_screen)
        self.background = Background(self.game_display)
        self.game_map = Map(self.game_display, self.screen_dims, 32)

    def setupPlayer(self):
        ''' Sets up player for the first level
        '''
        self.player = Player(self.game_display, self.game_map, 
                                            self.player_x, - 100)
        self.player_group = pygame.sprite.Group()
        self.player_group.add(self.player)
        self.characters = pygame.sprite.Group()
        self.characters.add(self.player)

    def addCameraTracking(self):
        '''
        Method to add all blitted objects to camera
        '''
        self.camera.addBack(self.background)
        self.camera.addMap(self.game_map)
        self.camera.addPlayer(self.player)
        for enemy in self.enemy_group:
            self.camera.add(enemy)

    def decideEnemyType(self):
        '''
        Randomly returns an enemy from the enemies list
        Consulted docs below to check how to use randint vs randrange
        https://docs.python.org/3/library/random.html
        '''
        idx = random.randrange(len(ENEMIES))
        return ENEMIES[idx]

    def decideRandomArm(self):
        '''
        Randomly determine which arms to give an enemy
        '''
        idx = random.randrange(len(self.weapon_types))
        return self.weapon_types[idx]

    def generateLevel(self):
        '''
        This function generates a new level, and enemies to fight
        '''
        # Setup enemy group for level
        self.enemy_group = pygame.sprite.Group()
        self.dropped_weapons = pygame.sprite.Group()
        # Set up enemies for level.  Level number represents number of 
        # enemies
        for n in range(self.level.val):
            enemy_type = self.decideEnemyType()
            position = random.randrange(self.spawn_area[0], self.spawn_area[1])
            enemy = NPC(self.game_display, self.game_map, position, -100, 
                                        enemy_type, self.decideRandomArm())
            enemy.addTarget(self.player_group)
            self.enemy_group.add(enemy)
            self.characters.add(enemy)

        # Tell player about enemies
        self.player.addTarget(self.enemy_group)

        # Setup tracking
        self.addCameraTracking()

    def resetPlayer(self):
        ''' Resets player to start point for new level
        '''
        self.player.changeMap(self.game_map)
        self.player.center = self.player_x, -100
        self.player.updateState('idle', self.player.state[1])
        self.player.x_y_moving = False
        self.player.max_health += 10
        self.player.health = self.player.max_health

    def firstLevel(self):
        ''' Sets up first level
        '''
        introScreen(self.game_screen, self)
        self.setupCameraMap()
        self.setupPlayer()
        self.generateLevel()

    def newLevel(self):
        ''' Function to start a new level

        Increments the level counter, and adjusts player health
        '''
        self.level.val += 1
        self.level_complete = False
        self.setupCameraMap()
        self.resetPlayer()
        self.generateLevel()

    def keyboardInput(self, event):
        ''' keyboardInput

        Called by game loop, and checking events from keyboard, and
        calling respective functions.
        Includes functionality to activate 'god mode'.
        The intention of god mode is for debugging without dying.

        We initially used the syntax:
        if event.key == pygame.K_w:
                self.player.startMove("u")
        However by browing through the documentation, we discovered that
        with pygame 2.0.0 there was a new feature:
            pygame.key.key_code().
        We can pass in the string of the key eg "space" for space, or
        "w" for "w".
        This allows us to easily produce a human readable JSON
        containing the keybindings so that the user can change the
        keybindings to those of their choice.

        We load this JSON each time we instantiate this class, as the
        intention is that if we have time between now and submission, we
        will produce a settings screen to allow the user to graphically
        change the keybindings to their preference.
        '''
        if event.type == pygame.KEYDOWN:
            # WASD for up/right/left, q for attack
            if event.key == pygame.key.key_code(self.settings['up']):
                self.player.startMove("u")
            elif event.key == pygame.key.key_code(self.settings['right']):
                self.player.startMove("r")
            elif event.key == pygame.key.key_code(self.settings['left']):
                self.player.startMove("l")
            elif event.key == pygame.key.key_code(self.settings['attack']):
                self.player.attack()
            # When level complete, space to move to next level
            elif (event.key == pygame.key.key_code(self.settings['next_level']))\
                                            and self.level_complete:
                self.newLevel()
            # Escape to pause game
            elif event.key == pygame.K_ESCAPE:
                self.player.updateState('idle', self.player.state[1])
                self.player.x_y_moving = False
                pauseScreen(self.game_screen, self)
            # Enter cheat code to enter god mode
            elif event.key == pygame.K_RSHIFT:
                self.cheats = 1
            elif (event.key == pygame.K_1) and (self.cheats == 1):
                self.cheats += 1
            elif (event.key == pygame.K_2) and (self.cheats == 2):
                self.cheats += 1
            elif (event.key == pygame.K_3) and (self.cheats == 3):
                self.cheats += 1

        elif event.type == pygame.KEYUP:
            # Toggle right/left moving
            if event.key == pygame.key.key_code(self.settings['right']):
                self.player.stopMoveX("right")
            elif event.key == pygame.key.key_code(self.settings['left']):
                self.player.stopMoveX("left")
            # Lift right shift to submit code for god mode
            elif event.key == pygame.K_RSHIFT:
                if self.cheats == 4:
                    self.initGodMode()
                    self.cheats = 0
                else:
                    self.cheats = 0

    def initGodMode(self):
        ''' God Mode

        This is here to debug the game without dying, and without having
        to edit the code.
        '''
        self.god_mode = True
        self.player.max_health = 1000000000000000000000000000
        self.player.health = self.player.max_health
        self.gt = Text(self.game_screen,
                        (110, self.game_screen.get_height() - 20),
                                        20, 'god mode activated')
        self.player.arms.strength *= 10000

    def update(self):
        ''' Update function - Used to update positions of characters on
            screen.

            This was initially encapsulated in the display function,
            however this caused issues when the map functions were
            tracking characters.  This was due to the fact that some
            changes to the characters position (such as due to gravity
            and recoil) were being applied after the map had updated.
            To avoid this, update functions were added to characters.
            These are called before we blit to the screen.
        '''
        

        # Updating character positions
        for character in self.characters:
            character.update()
            for projectile in character.thrown_projectiles:
                # Get any new projectiles and add to camera
                if not self.projectiles.has(projectile):
                    self.projectiles.add(projectile)
                    self.camera.addWeapon(projectile)
        
        # update tracked projectiles
        for projectile in self.projectiles:
            # If projectile off screen, remove from sprite groups
            if (projectile.rect.centerx < 0) or \
                    (projectile.rect.centerx > self.map_width):
                projectile.kill()
            projectile.update()

        for weapon in self.dropped_weapons:
            weapon.update()

        # Check if player is alive
        if self.player.alive == False:
            # End game
            self.run = False
            gameOver(self.game_screen, self.player.score, self.clock_delay)

        for enemy in self.enemy_group:
            if enemy.rect.bottom > self.screen_dims[1]:
                enemy.kill()
            if enemy.alive == False:
                self.camera.addWeapon(enemy.arms)
                self.dropped_weapons.add(enemy.arms)
                enemy.arms.addCharacterGroup(self.characters)
                enemy.kill()

        if len(self.enemy_group) == 0:
            self.level_complete = True

        #self.score_string.text = f'Score = {self.player.score}'
        self.score.val = self.player.score

        # Update camera position
        self.camera.scroll()

    def display(self):
        ''' Display

        This displays all our objects to the screen in order.  This
        takes place each frame.
        '''

        # Colour screen purple
        self.game_display.fill(self.colour['skyblue'])

        # Display background and map
        self.background.displayQ()
        self.game_map.display()

        # Display characters
        for enemy in self.enemy_group:
            enemy.display()
        
        self.player.display()

        for weapon in self.dropped_weapons:
            weapon.display()

        #print(self.projectiles)
        for projectile in self.projectiles:
            projectile.display()

        # scales the game_display to game_screen. Allows us to scale 
        # images
        scaled_surf = pygame.transform.scale(self.game_display,
                                                self.screen_dims)
        self.game_screen.blit(scaled_surf, (0, 0))

        self.score.display()
        self.level.display()

        # If in god mode, display text
        if self.god_mode:
            self.gt.display()

        # If waiting to change level, display text
        if self.level_complete:
            self.level_complete_text_1.display()
            self.level_complete_text_2.display()

        # Camera variable to create camera movement


# These three classes are used to produce a score and level output on 
# the screen during gameplay
# Refactored from main Controller class by Robert

class GameOutput():
    ''' GameOutput

    Class to deal with displaying score and level to the game
    '''
    font_size = 30

    def __init__(self, screen):
        '''
        Initialises a Text object on the screen which can be updated
        when required
        '''
        self.text_output = Text(screen, (self.position), self.font_size,
                                                             str(self))

    def __str__(self):
        '''
        Returns a string of the label and value
        '''
        return f'{self.label}{self.val}'

    def refreshString(self):
        '''
        Refreshes the string to blit each time value is changed
        '''
        self.text_output.text = str(self)

    def display(self):
        '''
        Blits text object to string
        '''
        self.text_output.display()


class Score(GameOutput):
    '''
    Shows score on screen at top left.

    We store the value as a private variable, this is so we can use the
    setter decorator to control how it is updated.  To avoid making our
    characters depend on this class, they never update the object.
    Instead the controller updates the value with each update.
    To avoid having to re-render the Text object every update, we check
    whether the score has changed, if it has we update it and re-render
    the Text object.
    '''

    def __init__(self, screen):
        self.position = (100, 50)
        self.__val = 0
        self.label = 'Score: '
        GameOutput.__init__(self, screen)

    @property
    def val(self):
        return self.__val

    @val.setter
    def val(self, new_val):
        if new_val == self.__val:
            return
        else:
            self.__val = new_val
            self.refreshString()

class Level(GameOutput):
    '''
    Used to display Level we are on to top right hand side of screen

    Frustratingly we had to copy and paste the @property method and
    couldn't use inheritance.  This is because the __val attribute is
    private and cannot be accessed outside of the Level class.
    (Sorry about copying code! We really didn't have a choice :'( )

    The value setter is similar to the setter in Score, however we don't
    bother checking if there is a change in level before updating it as
    we will only be updating this class when there is a change.
    '''
    def __init__(self, screen):
        #(100, 100), 20, 'Score = 0'
        self.position = (screen.get_width() - 100 , 50)
        self.__val = 1
        self.label = 'Level: '
        GameOutput.__init__(self, screen)

    @property
    def val(self):
        return self.__val

    @val.setter
    def val(self, new_val):
        self.__val = new_val
        self.refreshString()
