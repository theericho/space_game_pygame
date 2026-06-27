"""
Models module for Space Invaders

This module contains the model classes for the Space Invaders game. Anything
that you interact with on the screen is a model: the ship, the laser bolts, and
the aliens. Each model stores its center (x, y) and exposes a pygame ``Rect``
that is used for drawing and collision tests.
"""
import pygame

from consts import *


class Ship(object):
    """
    A class to represent the game ship.
    """
    # Attribute image: the ship sprite
    # Invariant: image is a pygame Surface
    #
    # Attribute width: the width of the ship in pixels
    # Invariant: width is an int or float
    #
    # Attribute height: the height of the ship in pixels
    # Invariant: height is an int or float
    #
    # Attribute x: the x-coordinate of the ship center
    # Invariant: x is an int or float
    #
    # Attribute y: the y-coordinate of the ship center
    # Invariant: y is an int or float

    # INITIALIZER TO CREATE A NEW SHIP
    def __init__(self, image):
        """
        Initializes the ship at the bottom center of the window.

        Parameter image: the ship sprite
        Precondition: image is a pygame Surface
        """
        self.image = image
        self.width = SHIP_WIDTH
        self.height = SHIP_HEIGHT
        self.x = GAME_WIDTH / 2
        self.y = GAME_HEIGHT - SHIP_BOTTOM - SHIP_HEIGHT / 2

    # METHODS TO DRAW THE SHIP AND CHECK FOR COLLISIONS
    def rect(self):
        """
        Returns the bounding box of the ship as a pygame Rect.
        """
        return self.image.get_rect(center=(self.x, self.y))

    def draw(self, surface):
        """
        Draws the ship onto the given surface.

        Parameter surface: the surface to draw on
        Precondition: surface is a pygame Surface
        """
        surface.blit(self.image, self.rect())

    def collides(self, bolt):
        """
        Returns True if an alien bolt collides with the ship.

        This method returns False if the bolt was fired by the player.

        Parameter bolt: the laser bolt to check
        Precondition: bolt is a Bolt object
        """
        return (not bolt.is_player) and self.rect().colliderect(bolt.rect())


class Alien(object):
    """
    A class to represent a single alien.
    """
    # Attribute image: the alien sprite
    # Invariant: image is a pygame Surface
    #
    # Attribute x: the x-coordinate of the alien center
    # Invariant: x is an int or float
    #
    # Attribute y: the y-coordinate of the alien center
    # Invariant: y is an int or float
    #
    # Attribute width: the width of the alien in pixels
    # Invariant: width is an int or float
    #
    # Attribute height: the height of the alien in pixels
    # Invariant: height is an int or float

    # INITIALIZER TO CREATE AN ALIEN
    def __init__(self, x, y, image):
        """
        Initializes an alien centered at the given position.

        Parameter x: the center x value of the alien
        Precondition: x is a number (int or float)

        Parameter y: the center y value of the alien
        Precondition: y is a number (int or float)

        Parameter image: the alien sprite
        Precondition: image is a pygame Surface
        """
        self.image = image
        self.x = x
        self.y = y
        self.width = ALIEN_WIDTH
        self.height = ALIEN_HEIGHT

    # METHODS TO DRAW THE ALIEN AND CHECK FOR COLLISIONS
    def rect(self):
        """
        Returns the bounding box of the alien as a pygame Rect.
        """
        return self.image.get_rect(center=(self.x, self.y))

    def draw(self, surface):
        """
        Draws the alien onto the given surface.

        Parameter surface: the surface to draw on
        Precondition: surface is a pygame Surface
        """
        surface.blit(self.image, self.rect())

    def collides(self, bolt):
        """
        Returns True if a player bolt collides with this alien.

        This method returns False if the bolt was fired by an alien.

        Parameter bolt: the laser bolt to check
        Precondition: bolt is a Bolt object
        """
        return bolt.is_player and self.rect().colliderect(bolt.rect())


class Bolt(object):
    """
    A class representing a laser bolt.

    A bolt with negative velocity travels up the screen and is a player bolt;
    a bolt with positive velocity travels down and is an alien bolt.
    """
    # Attribute x: the x-coordinate of the bolt center
    # Invariant: x is an int or float
    #
    # Attribute y: the y-coordinate of the bolt center
    # Invariant: y is an int or float
    #
    # Attribute velocity: the signed vertical speed (negative = up = player bolt)
    # Invariant: velocity is an int or float
    #
    # Attribute color: the (r, g, b) fill color of the bolt
    # Invariant: color is a tuple of three ints in 0..255
    #
    # Attribute is_player: whether the bolt was fired by the player
    # Invariant: is_player is a bool (True or False)

    # INITIALIZER TO SET THE POSITION, VELOCITY, AND COLOR
    def __init__(self, x, y, velocity, color):
        """
        Initializes the bolt.

        Parameter x: the center x value of the bolt
        Precondition: x is a number (int or float)

        Parameter y: the center y value of the bolt
        Precondition: y is a number (int or float)

        Parameter velocity: the signed vertical speed (negative = up = player bolt)
        Precondition: velocity is a number (int or float)

        Parameter color: the (r, g, b) fill color
        Precondition: color is a tuple of three ints in 0..255
        """
        self.x = x
        self.y = y
        self.width = BOLT_WIDTH
        self.height = BOLT_HEIGHT
        self.velocity = velocity
        self.color = color
        self.is_player = velocity < 0

    # METHODS TO MOVE, TEST, AND DRAW THE BOLT
    def rect(self):
        """
        Returns the bounding box of the bolt as a pygame Rect.
        """
        return pygame.Rect(self.x - self.width / 2, self.y - self.height / 2,
                           self.width, self.height)

    def move(self):
        """
        Advances the bolt by its velocity.
        """
        self.y += self.velocity

    def offscreen(self):
        """
        Returns True once the bolt has left the window vertically.
        """
        return self.y < 0 or self.y > GAME_HEIGHT

    def draw(self, surface):
        """
        Draws the bolt onto the given surface.

        Parameter surface: the surface to draw on
        Precondition: surface is a pygame Surface
        """
        pygame.draw.rect(surface, self.color, self.rect())
