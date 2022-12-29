''' Weapon Class
- To have a subclass for each weapon.
@author: Shaylen Mistry (unless stated otherwise)
worked with Robert to help prototype code
'''
import pygame
from classes.spritesheet import SpriteSheet
from classes.sfxbox import SFXBox


SFX = SFXBox()

# From spritesheet import SpriteSheet
# Arms spirtesheets
BASIC_ARMS_LOCATION = 'graphics/spritesheets/basic-arms.png'
SWORD_ARMS_LOCATION = 'graphics/spritesheets/sword-arms.png'
BOOMERANG_ARMS_LOCATION = 'graphics/spritesheets/boomerang-arms.png'

# Boomerang Animation
BOOMERANG_ANIMATION_LOCATION = 'graphics/weapons/boomerang.png'

# Static images
SWORD_LOCATION = 'graphics/weapons/sword.png'
BOOMERANG_LOCATION = 'graphics/weapons/boomerang-static.png'


# Superclass of weapon
class Weapon(pygame.sprite.Sprite):
    def __init__(self, owner, sprite_sheet_location):
        pygame.sprite.Sprite.__init__(self)
        self.owner = owner
        self.screen = owner.screen        
        self.owned = True

        # Loading Sprite Sheet
        image_types = owner.character_data['actions']
        image_directions = owner.character_data['directions']
        char_size = [32, 32]
        scaled_size = owner.scaled_size
        coords = owner.character_data
    
        self.loadSpriteSheets(image_types, image_directions, scaled_size,
                                char_size, coords, sprite_sheet_location)

        # Setting up initial image
        self.state = owner.state
        self.image = self.images[self.state[0]][self.state[1]]
        self.index = owner.image_index
        self.rect = self.image[self.index].get_rect()
        self.rect.centerx = self.owner.rect.centerx
        self.rect.centery = self.owner.rect.centery


   # Assinging animation images to self 
    def loadSpriteSheets(self, image_types, image_directions, scaled_size, 
                        char_size, coords, sprite_sheet_location,
                        background_colour = (0, 255, 0)):
            
        self.spritesheet = SpriteSheet(sprite_sheet_location)
        self.images = {}
        for image_type in image_types:
            self.images[image_type] = {}
            for image_direction in image_directions:
                self.images[image_type][image_direction] = []
                for coord in coords[image_type][image_direction]:
                    specific_image = pygame.transform.scale(
                            self.spritesheet.image_at(coord, char_size),
                            scaled_size
                            )
                    specific_image.set_colorkey(background_colour)

                    self.images[image_type][image_direction] += \
                                                             [specific_image]


    def addCharacterGroup(self, char_group):
        self.characters = char_group


    def display(self):
        ''' display function

        state takes form [action, direction], images[action][direction]
        gives a list of images
        '''

        
        # Get owner variables
        self.state = self.owner.state
        self.index = self.owner.image_index
        action, direction = self.state[0], self.state[1]

        # Select Image
        self.image = self.images[action][direction]

        self.rect.center = self.owner.rect.center
    
        # Rect position alive
        if self.owner.alive:
            
            self.screen.blit(self.image[self.index], self.rect)
        else:
            self.owned = False 
        
    # Attack function for weapon
    def attack(self, direction, target):
        if target.health < self.strength:
            self.owner.score += target.health
        else:
            self.owner.score += self.strength
        self.sound()
        target.recoil(self.strength, direction)

# Drops weapon where npc dies
class DroppableWeapon(Weapon):
    droppable = True
    def display(self):
        ''' Display function used to blit weapon where npc dies
        '''
        if self.owned:
            Weapon.display(self)
        else:
            self.screen.blit(self.weapon, self.rect) 

    def updateUses(self):
        ''' Sets a weapon use capacity
        '''
        self.uses+=1
        if self.uses == self.owner.max_uses:
            self.kill()
            self.owner.arms = Arms(self.owner)

    # Collisions between player and weapon
    def update(self):
        ''' Ensures that when the player collides with a dropped weapon,
        it picks it up for use
        '''
        collisions = pygame.sprite.spritecollide(self, self.characters, False)
        if len(collisions) > 0:
            for character in collisions:
                if not character.arms.droppable:
                    self.kill()
                    character.setArms(self)
                    self.owned = True
                    self.owner = character
                    self.uses = 0
                    return

class Sword(DroppableWeapon):
    sprite_sheet_location = SWORD_ARMS_LOCATION
    strength = 15
    projectile = False
    uses = 0
    sound = SFX.wind
    def __init__(self, owner):
        Weapon.__init__(self, owner, self.sprite_sheet_location)
    
        self.weapon = pygame.image.load(SWORD_LOCATION)
        self.weapon.set_colorkey((0, 255, 0))

    def attack(self, direction, target):
        self.updateUses()
        Weapon.attack(self, direction, target)

class Boomerang(DroppableWeapon):
    sprite_sheet_location = BOOMERANG_ARMS_LOCATION
    strength = 15
    projectile = True
    uses = 0
    sound = SFX.wind
    def __init__(self, owner):
        Weapon.__init__(self, owner, self.sprite_sheet_location)

        self.weapon = pygame.image.load(BOOMERANG_LOCATION)
        self.weapon.set_colorkey((0, 255, 0))
    
    def throw(self, direction):
        self.updateUses()
        self.sound()
        return BoomerangAmmo(self.owner, self.owner.target_group,
                            self.strength, direction)

class Arms(Weapon):
    sprite_sheet_location = BASIC_ARMS_LOCATION
    strength = 10
    projectile = False
    droppable = False
    sound = SFX.punch
    def __init__(self, owner):
        Weapon.__init__(self, owner, self.sprite_sheet_location)

# Animation for boomerang throw
class BoomerangAmmo(pygame.sprite.Sprite):
    def __init__(self, owner, characters, strength, direction):
        pygame.sprite.Sprite.__init__(self)
        self.loadFrames()
        self.group = characters
        self.owner = owner
        self.strength = strength
        self.screen = self.owner.screen

        if direction == 'left':
            self.speed = -3
        else:
            self.speed = 3

        self.frame_rate = 10
        self.frame_counter = 0
        self.period = 1
        self.period_counter = 0

        self.rect.center = self.owner.rect.center

    def loadFrames(self):
        self.frames = []
        self.spritesheet = SpriteSheet(BOOMERANG_ANIMATION_LOCATION)
        for i in range(4):
            frame = self.spritesheet.image_at((i, 0), (32, 32), (0, 255, 0))
            self.frames.append(frame)
        self.current_frame = 0
        self.num_frames = len(self.frames)
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect()
    
    def update(self):

        self.period_counter += 1
        if self.period_counter == self.period:
            self.rect.centerx += self.speed
            self.period_counter = 0
        self.frame_counter += 1

        if self.frame_counter == self.frame_rate:
            self.current_frame += 1
            self.frame_counter = 0
        
        
        if self.current_frame >= len(self.frames):
            self.current_frame = 0

        collisions = pygame.sprite.spritecollide(self, self.group, False)
        
        if collisions != None:
            for sprite in collisions:
                if self.rect.centerx < sprite.rect.centerx:
                    direction = 1
                else:
                    direction = -1
                sprite.recoil(self.strength, direction)
                self.owner.score += self.strength
                self.kill()
            
            
    def display(self):
        self.image = self.frames[self.current_frame]
        self.screen.blit(self.image, self.rect)


WEAPON_TYPES = {
    'arms':Arms,
    'boomerang':Boomerang,
    'sword':Sword
}