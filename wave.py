"""
Subcontroller module for Space Invaders

This module contains the subcontroller to manage a single wave in the Space
Invaders game. A Wave owns the ship, the grid of aliens, and the laser bolts.
It marches the aliens back and forth, fires bolts, resolves collisions, tracks
lives, and plays sound effects through a shared sound manager.
"""
import random

import pygame

from consts import *
from models import Ship, Alien, Bolt


class Wave(object):
    """
    This class controls a single level or wave of Space Invaders.
    """
    # Attribute images: the dict mapping sprite names to pygame Surfaces
    # Invariant: images is a dict of str -> pygame Surface
    #
    # Attribute sound: the shared sound manager used for all effects
    # Invariant: sound is a SoundManager
    #
    # Attribute ship: the player ship to control
    # Invariant: ship is a Ship object or None
    #
    # Attribute aliens: the 2d list of aliens in the wave
    # Invariant: aliens is a rectangular 2d list of Alien objects or None
    #
    # Attribute bolts: the laser bolts currently on screen
    # Invariant: bolts is a list of Bolt objects, possibly empty
    #
    # Attribute moving_right: whether the aliens are marching right
    # Invariant: moving_right is a bool (True or False)
    #
    # Attribute time: the seconds elapsed since the last alien step
    # Invariant: time is a float >= 0
    #
    # Attribute movecount: the number of alien steps taken since the last bolt
    # Invariant: movecount is an int >= 0
    #
    # Attribute stepthresh: the alien steps to wait before the next alien bolt
    # Invariant: stepthresh is an int >= 0
    #
    # Attribute collist: the column indices still able to fire an alien bolt
    # Invariant: collist is a list of ints
    #
    # Attribute lives: the number of lives left
    # Invariant: lives is an int >= 0
    #
    # Attribute pause: whether the controller should pause the game
    # Invariant: pause is a bool (True or False)
    #
    # Attribute trigger_respawn: whether the ship is waiting to respawn
    # Invariant: trigger_respawn is a bool (True or False)
    #
    # Attribute all_dead: whether every alien has been destroyed
    # Invariant: all_dead is a bool (True or False)
    #
    # Attribute crossed: whether an alien has reached the defensive line
    # Invariant: crossed is a bool (True or False)
    #
    # Attribute wavecounter: the number of waves already completed
    # Invariant: wavecounter is an int >= 0
    #
    # Attribute wavespeed: the number of seconds between alien steps
    # Invariant: wavespeed is a float > 0
    #
    # Attribute score: the current number of points the player has
    # Invariant: score is an int >= 0
    #
    # Attribute just_killed: whether an alien was just killed this frame
    # Invariant: just_killed is a bool (True or False)
    #
    # Attribute defense_y: the y-coordinate of the defensive line
    # Invariant: defense_y is an int or float

    # INITIALIZER (standard form) TO CREATE SHIP AND ALIENS
    def __init__(self, wavecounter, score, images, sound):
        """
        Initializes the wave.

        The ship, aliens, bolt list, and all of the bookkeeping attributes are
        assigned. The wave speeds up by ALIEN_SP_DEC for every completed wave.

        Parameter wavecounter: the number of waves already completed
        Precondition: wavecounter is an int >= 0

        Parameter score: the running point total carried into this wave
        Precondition: score is an int >= 0 in multiples of 10

        Parameter images: the dict mapping sprite names to pygame Surfaces
        Precondition: images is a dict of str -> pygame Surface

        Parameter sound: the shared sound manager
        Precondition: sound is a SoundManager
        """
        self.images = images
        self.sound = sound

        self.ship = Ship(images['ship'])
        self.aliens = self._make_aliens()
        self.bolts = []
        self.moving_right = True

        self.time = 0.0
        self.movecount = 0
        self.stepthresh = random.randint(1, BOLT_RATE)
        self.collist = list(range(ALIENS_IN_ROW))

        self.lives = SHIP_LIVES
        self.pause = False
        self.trigger_respawn = False
        self.all_dead = False
        self.crossed = False

        self.wavecounter = wavecounter
        self.wavespeed = ALIEN_SPEED - (self.wavecounter * ALIEN_SP_DEC)
        if self.wavespeed <= 0:
            self.wavespeed = 0.1
        self.score = score
        self.just_killed = False

        self.defense_y = GAME_HEIGHT - DEFENSE_LINE

    # HELPER METHOD TO BUILD THE ALIEN GRID
    def _make_aliens(self):
        """
        Builds and returns the 2d list of aliens, with row 0 at the top.

        Each row uses one of the alien images, and the rows are spaced by
        ALIEN_V_SEP while the columns are spaced by ALIEN_H_SEP.
        """
        grid = []
        for r in range(ALIEN_ROWS):
            row = []
            y = ALIEN_CEILING + ALIEN_HEIGHT / 2 + r * (ALIEN_HEIGHT + ALIEN_V_SEP)
            image = self.images[ALIEN_IMAGES[r // 2 % 3]]
            for c in range(ALIENS_IN_ROW):
                x = ALIEN_H_SEP + ALIEN_WIDTH / 2 + c * (ALIEN_H_SEP + ALIEN_WIDTH)
                row.append(Alien(x, y, image))
            grid.append(row)
        return grid

    # PUBLIC METHOD FOR THE CONTROLLER
    def respawn_ship(self):
        """
        Recreates the ship in the center, used when continuing after a death.
        """
        self.ship = Ship(self.images['ship'])
        self.trigger_respawn = False

    # UPDATE METHOD TO MOVE THE SHIP, ALIENS, AND LASER BOLTS
    def update(self, dt, keys):
        """
        Advances the wave by one frame.

        This moves the ship and aliens, fires and moves bolts, resolves
        collisions, and tracks the player's lives.

        Parameter dt: the time in seconds since the last frame
        Precondition: dt is a number (int or float)

        Parameter keys: the pygame held-key state (pygame.key.get_pressed())
        Precondition: keys is indexable by pygame key constants
        """
        self._check_all_dead()
        self._check_alien_pos()
        self._move_ship(keys)
        self._alien_walk(dt)
        self._make_bolt(keys)
        self._make_alien_bolt()
        self._move_bolts()
        self._collisions()
        self._track_lives()
        self._respawn_ship()

    # DRAW METHOD TO DRAW THE ALIENS, SHIP, DEFENSIVE LINE, AND BOLTS
    def draw(self, surface):
        """
        Draws the aliens, ship, defensive line, and bolts.

        Parameter surface: the surface to draw on
        Precondition: surface is a pygame Surface
        """
        for row in self.aliens:
            for alien in row:
                if alien is not None:
                    alien.draw(surface)
        if self.ship is not None:
            self.ship.draw(surface)
        pygame.draw.line(surface, COLOR_LINE, (0, self.defense_y),
                         (GAME_WIDTH, self.defense_y), 2)
        for bolt in self.bolts:
            bolt.draw(surface)

    # HELPER METHODS
    def _move_ship(self, keys):
        """
        Moves the ship with the arrow keys or A/D, clamped to the window.

        Parameter keys: the pygame held-key state
        Precondition: keys is indexable by pygame key constants
        """
        if self.ship is None:
            return
        left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        if left and self.ship.x - SHIP_MOVEMENT >= SHIP_WIDTH / 2:
            self.ship.x -= SHIP_MOVEMENT
        if right and self.ship.x + SHIP_MOVEMENT <= GAME_WIDTH - SHIP_WIDTH / 2:
            self.ship.x += SHIP_MOVEMENT

    def _alien_walk(self, dt):
        """
        Steps the aliens horizontally, dropping and reversing at the edges.

        The aliens only take a step once enough time (wavespeed) has elapsed.
        When the leading alien reaches an edge, every alien drops down by
        ALIEN_V_WALK and the marching direction reverses.

        Parameter dt: the time in seconds since the last frame
        Precondition: dt is a number (int or float)
        """
        self.time += dt
        if self.time < self.wavespeed:
            return
        self.time = 0.0
        self.movecount += 1
        edge = self._edge_alien()
        if edge is None:
            return
        at_right = (self.moving_right and
                    edge.x + ALIEN_H_WALK + ALIEN_WIDTH / 2 >= GAME_WIDTH - ALIEN_H_SEP)
        at_left = (not self.moving_right and
                   edge.x - ALIEN_H_WALK - ALIEN_WIDTH / 2 <= ALIEN_H_SEP)
        if at_right or at_left:
            for row in self.aliens:
                for alien in row:
                    if alien is not None:
                        alien.y += ALIEN_V_WALK
            self.moving_right = not self.moving_right
        else:
            direction = 1 if self.moving_right else -1
            for row in self.aliens:
                for alien in row:
                    if alien is not None:
                        alien.x += ALIEN_H_WALK * direction

    def _edge_alien(self):
        """
        Returns the left-most or right-most living alien (whichever leads).

        Returns None if there are no living aliens.
        """
        cols = range(ALIENS_IN_ROW - 1, -1, -1) if self.moving_right else range(ALIENS_IN_ROW)
        for c in cols:
            for r in range(ALIEN_ROWS):
                if self.aliens[r][c] is not None:
                    return self.aliens[r][c]
        return None

    def _make_bolt(self, keys):
        """
        Fires a player bolt when SPACE is held, if none is already on screen.

        Only one player bolt may exist at a time, so the player must wait for
        the previous bolt to leave the window or hit an alien.

        Parameter keys: the pygame held-key state
        Precondition: keys is indexable by pygame key constants
        """
        if self.ship is None:
            return
        if not keys[pygame.K_SPACE]:
            return
        if any(b.is_player for b in self.bolts):
            return
        self.bolts.append(Bolt(self.ship.x, self.ship.y - SHIP_HEIGHT / 2 - BOLT_HEIGHT / 2,
                               -BOLT_SPEED, COLOR_PBOLT))
        self.sound.play('ship_fire')

    def _make_alien_bolt(self):
        """
        Fires a bolt from a random column's bottom alien once the timer is up.

        Columns with no living aliens are removed from the candidate list so
        that they cannot be chosen to fire.
        """
        while self.collist and self.movecount == self.stepthresh:
            col = random.choice(self.collist)
            alien = self._bottom_alien(col)
            if alien is None:
                self.collist.remove(col)
            else:
                self.bolts.append(Bolt(alien.x, alien.y + ALIEN_HEIGHT / 2 + BOLT_HEIGHT / 2,
                                       BOLT_SPEED, COLOR_ABOLT))
                self.sound.play('alien_fire')
                self.movecount = 0
                self.stepthresh = random.randint(1, BOLT_RATE)

    def _bottom_alien(self, col):
        """
        Returns the lowest (closest to the player) living alien in a column.

        Returns None if the column has no living aliens.

        Parameter col: the column index to search
        Precondition: col is an int in range 0..ALIENS_IN_ROW-1
        """
        for r in range(ALIEN_ROWS - 1, -1, -1):
            if self.aliens[r][col] is not None:
                return self.aliens[r][col]
        return None

    def _move_bolts(self):
        """
        Moves every bolt and removes the ones that have left the window.
        """
        for bolt in self.bolts:
            bolt.move()
        self.bolts = [b for b in self.bolts if not b.offscreen()]

    # HELPER METHODS FOR COLLISION DETECTION
    def _collisions(self):
        """
        Resolves player-bolt/alien and alien-bolt/ship collisions.

        A player bolt that hits an alien removes both, adds to the score, and
        speeds the wave up. An alien bolt that hits the ship destroys the ship.
        """
        for r in range(ALIEN_ROWS):
            for c in range(ALIENS_IN_ROW):
                alien = self.aliens[r][c]
                if alien is None:
                    continue
                for bolt in self.bolts:
                    if bolt.is_player and alien.collides(bolt):
                        self.aliens[r][c] = None
                        self.bolts.remove(bolt)
                        self.score += self._points(r)
                        self.wavespeed *= INCREMENT
                        self.just_killed = True
                        self.sound.play('alien_death')
                        break
        if self.ship is not None:
            for bolt in list(self.bolts):
                if (not bolt.is_player) and self.ship.collides(bolt):
                    self.bolts.remove(bolt)
                    self.sound.play('ship_death')
                    self.ship = None
                    break

    def _points(self, row):
        """
        Returns the points for killing an alien in the given row.

        Aliens in higher rows (smaller row index) are worth more points.

        Parameter row: the row index of the killed alien
        Precondition: row is an int in range 0..ALIEN_ROWS-1
        """
        return ((ALIEN_ROWS - 1 - row) // 2 + 1) * 10

    def _track_lives(self):
        """
        Decrements a life and requests a pause when the ship is destroyed.
        """
        if self.ship is None and not self.pause and not self.trigger_respawn:
            self.lives -= 1
            self.pause = True
            self.trigger_respawn = True

    def _respawn_ship(self):
        """
        Respawns the ship once the controller has cleared the pause.
        """
        if self.ship is None and not self.pause and self.trigger_respawn:
            self.respawn_ship()

    def _check_all_dead(self):
        """
        Sets all_dead to True when no living aliens remain.
        """
        for row in self.aliens:
            for alien in row:
                if alien is not None:
                    return
        self.all_dead = True

    def _check_alien_pos(self):
        """
        Sets crossed to True when any alien reaches the defensive line.
        """
        for row in self.aliens:
            for alien in row:
                if alien is not None and alien.y + ALIEN_HEIGHT / 2 >= self.defense_y:
                    self.crossed = True
                    return
