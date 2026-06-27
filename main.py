"""
Primary module for Space Invaders

This module owns the main game loop, the high-level state machine, asset
loading, and sound. The loop is written with asyncio so the same file runs both
natively (``python main.py``) and in the browser when compiled with pygbag.
"""
import asyncio
import os

import pygame

from consts import *
from wave import Wave

# the absolute path to the folder containing this module and its assets
BASE = os.path.dirname(os.path.abspath(__file__))


# ASSET AND PATH HELPERS
def _path(*parts):
    """
    Returns an absolute path to a bundled asset.

    Parameter parts: the path pieces to join onto the module folder
    Precondition: each part is a string
    """
    return os.path.join(BASE, *parts)


def load_images():
    """
    Loads and scales the sprites, returning a name -> Surface dict.

    This must be called after the display has been created so the images can be
    converted for fast blitting.
    """
    images = {}
    ship = pygame.image.load(_path('Images', 'ship.png')).convert_alpha()
    images['ship'] = pygame.transform.smoothscale(ship, (SHIP_WIDTH, SHIP_HEIGHT))
    for name in ALIEN_IMAGES:
        img = pygame.image.load(_path('Images', name)).convert_alpha()
        images[name] = pygame.transform.smoothscale(img, (ALIEN_WIDTH, ALIEN_HEIGHT))
    return images


def load_fonts():
    """
    Loads the arcade font in a few sizes, returning a name -> Font dict.

    If the font file cannot be loaded, a default system font is used instead.
    """
    sizes = {'big': 48, 'med': 30, 'small': 20}
    fonts = {}
    for key, size in sizes.items():
        try:
            fonts[key] = pygame.font.Font(_path('Fonts', 'Arcade.ttf'), size)
        except Exception:
            fonts[key] = pygame.font.SysFont(None, size)
    return fonts


# SOUND MANAGER
class SoundManager(object):
    """
    A class that loads sound effects and plays them, honoring a mute flag.
    """
    # Attribute muted: whether all sound effects are currently muted
    # Invariant: muted is a bool (True or False)
    #
    # Attribute sounds: the dict mapping names to loaded sounds (or None)
    # Invariant: sounds is a dict of str -> pygame Sound or None

    # INITIALIZER TO CREATE AN EMPTY SOUND LIBRARY
    def __init__(self):
        """
        Initializes an empty, unmuted sound manager.
        """
        self.muted = False
        self.sounds = {}

    # METHODS TO LOAD AND PLAY SOUNDS
    def load(self, name, filename):
        """
        Loads a single sound, storing None if it cannot be loaded.

        Parameter name: the key used to play the sound later
        Precondition: name is a string

        Parameter filename: the sound file name in the Sounds folder
        Precondition: filename is a string
        """
        try:
            self.sounds[name] = pygame.mixer.Sound(_path('Sounds', filename))
        except Exception:
            self.sounds[name] = None

    def load_all(self):
        """
        Loads every sound effect used by the game (OGG for browser support).
        """
        self.load('ship_fire', 'pew1.ogg')
        self.load('alien_fire', 'pew2.ogg')
        self.load('alien_death', 'pop2.ogg')
        self.load('ship_death', 'blast1.ogg')

    def play(self, name):
        """
        Plays the named sound unless it is missing or sounds are muted.

        Parameter name: the key of the sound to play
        Precondition: name is a string
        """
        sound = self.sounds.get(name)
        if sound is not None and not self.muted:
            try:
                sound.play()
            except Exception:
                pass

    def toggle_mute(self):
        """
        Flips the global mute state.
        """
        self.muted = not self.muted


# THE GAME CONTROLLER
class Game(object):
    """
    The primary controller class for the Space Invaders application.

    This class manages the game state (start screen, active, paused, complete)
    and drives the active Wave object.
    """
    # Attribute images: the dict mapping sprite names to pygame Surfaces
    # Invariant: images is a dict of str -> pygame Surface
    #
    # Attribute sound: the shared sound manager
    # Invariant: sound is a SoundManager
    #
    # Attribute fonts: the dict mapping size names to pygame Fonts
    # Invariant: fonts is a dict of str -> pygame Font
    #
    # Attribute state: the current game state
    # Invariant: state is one of the STATE_* constants
    #
    # Attribute wave: the subcontroller for the current wave
    # Invariant: wave is a Wave object, or None before the first wave
    #
    # Attribute wavecounter: the number of waves already completed
    # Invariant: wavecounter is an int >= 0
    #
    # Attribute scoretotal: the running point total across waves
    # Invariant: scoretotal is an int >= 0
    #
    # Attribute final_score: the score shown on the game-over screen
    # Invariant: final_score is an int >= 0
    #
    # Attribute message: the current centered message
    # Invariant: message is a string

    # INITIALIZER TO SET UP THE START SCREEN
    def __init__(self, images, sound, fonts):
        """
        Initializes the controller on the start screen.

        Parameter images: the dict mapping sprite names to pygame Surfaces
        Precondition: images is a dict of str -> pygame Surface

        Parameter sound: the shared sound manager
        Precondition: sound is a SoundManager

        Parameter fonts: the dict mapping size names to pygame Fonts
        Precondition: fonts is a dict of str -> pygame Font
        """
        self.images = images
        self.sound = sound
        self.fonts = fonts
        self.state = STATE_INACTIVE
        self.wave = None
        self.wavecounter = 0
        self.scoretotal = 0
        self.final_score = 0
        self.message = "Press 'S' to Play"

    # INPUT HANDLING
    def on_keydown(self, key):
        """
        Handles single-press keys: start/continue (S), pause (P), mute (M).

        Parameter key: the pygame key code that was pressed
        Precondition: key is a pygame key constant
        """
        if key == pygame.K_s:
            if self.state == STATE_INACTIVE:
                self.state = STATE_NEWWAVE
            elif self.state == STATE_PAUSED:
                self.state = STATE_CONTINUE
            elif self.state == STATE_COMPLETE:
                self._restart()
        elif key == pygame.K_p:
            if self.state == STATE_ACTIVE:
                self.state = STATE_MANUALPAUSE
            elif self.state == STATE_MANUALPAUSE:
                self.state = STATE_ACTIVE
        elif key == pygame.K_m:
            self.sound.toggle_mute()

    def _restart(self):
        """
        Starts a fresh game with the score reset to 0 (no menu in between).
        """
        self.wave = None
        self.wavecounter = 0
        self.scoretotal = 0
        self.final_score = 0
        self.state = STATE_NEWWAVE

    # UPDATE METHODS
    def update(self, dt, keys):
        """
        Advances the game one frame based on the current state.

        Parameter dt: the time in seconds since the last frame
        Precondition: dt is a number (int or float)

        Parameter keys: the pygame held-key state (pygame.key.get_pressed())
        Precondition: keys is indexable by pygame key constants
        """
        if self.state == STATE_NEWWAVE:
            self.wave = Wave(self.wavecounter, self.scoretotal, self.images, self.sound)
            self.state = STATE_ACTIVE
        if self.state == STATE_ACTIVE:
            self._update_active(dt, keys)
        elif self.state == STATE_CONTINUE:
            self.wave.update(dt, keys)
            self.state = STATE_ACTIVE

    def _update_active(self, dt, keys):
        """
        Runs the active wave and reacts to win/lose/pause conditions.

        Parameter dt: the time in seconds since the last frame
        Precondition: dt is a number (int or float)

        Parameter keys: the pygame held-key state
        Precondition: keys is indexable by pygame key constants
        """
        wave = self.wave
        wave.update(dt, keys)
        if wave.just_killed:
            self.scoretotal = wave.score
            wave.just_killed = False
        if wave.all_dead:
            self.wavecounter += 1
            self.state = STATE_NEWWAVE
            return
        if wave.crossed:
            self.state = STATE_COMPLETE
            self.message = "Aliens Breached! Game Over"
            self.final_score = wave.score
            return
        if wave.pause:
            if wave.lives > 0:
                self.state = STATE_PAUSED
                self.message = "Lives: %d   Press 'S' to Continue" % wave.lives
                wave.pause = False
            else:
                self.state = STATE_COMPLETE
                self.message = "Game Over"
                self.final_score = wave.score

    # DRAW METHODS
    def draw(self, screen):
        """
        Renders the current frame based on the current state.

        Parameter screen: the surface to draw on
        Precondition: screen is a pygame Surface
        """
        screen.fill(COLOR_BG)
        if self.state == STATE_INACTIVE:
            self._draw_center(screen, ["Space Invaders", self.message], 'big')
        elif self.state == STATE_ACTIVE:
            self.wave.draw(screen)
            self._draw_hud(screen)
        elif self.state == STATE_MANUALPAUSE:
            self.wave.draw(screen)
            self._draw_hud(screen)
            self._draw_center(screen, ["PAUSED", "Press 'P' to Resume"], 'med')
        elif self.state == STATE_PAUSED:
            self.wave.draw(screen)
            self._draw_hud(screen)
            self._draw_center(screen, [self.message], 'med')
        elif self.state == STATE_CONTINUE:
            self.wave.draw(screen)
            self._draw_hud(screen)
        elif self.state == STATE_COMPLETE:
            self._draw_center(screen, [self.message,
                                       "Points: %d" % self.final_score,
                                       "Press 'S' to Play Again"], 'med')

    def _draw_hud(self, screen):
        """
        Draws the lives / wave / score line, plus a mute indicator if muted.

        Parameter screen: the surface to draw on
        Precondition: screen is a pygame Surface
        """
        text = "Lives: %d   Wave: %d   Points: %d" % (
            self.wave.lives, self.wavecounter + 1, self.wave.score)
        surf = self.fonts['small'].render(text, True, COLOR_HUD)
        screen.blit(surf, (16, 12))
        if self.sound.muted:
            mute = self.fonts['small'].render("SOUND OFF (M)", True, COLOR_HUD)
            screen.blit(mute, (GAME_WIDTH - mute.get_width() - 16, 12))

    def _draw_center(self, screen, lines, font_key):
        """
        Draws one or more lines of text centered on the screen.

        Parameter screen: the surface to draw on
        Precondition: screen is a pygame Surface

        Parameter lines: the lines of text to draw, top to bottom
        Precondition: lines is a list of strings

        Parameter font_key: the size key into the fonts dict ('big'/'med'/'small')
        Precondition: font_key is a key in self.fonts
        """
        font = self.fonts[font_key]
        total = len(lines)
        for i, line in enumerate(lines):
            surf = font.render(line, True, COLOR_TEXT)
            cy = GAME_HEIGHT // 2 + (i - (total - 1) / 2) * (font.get_height() + 10)
            screen.blit(surf, surf.get_rect(center=(GAME_WIDTH // 2, cy)))


# THE MAIN GAME LOOP
async def main():
    """
    Sets up pygame and runs the game loop until the window is closed.

    The loop is asynchronous so the same code runs natively and in the browser
    when compiled with pygbag.
    """
    pygame.init()
    try:
        pygame.mixer.init()
    except Exception:
        pass

    screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
    pygame.display.set_caption("Space Invaders")
    clock = pygame.time.Clock()

    images = load_images()
    fonts = load_fonts()
    sound = SoundManager()
    sound.load_all()
    game = Game(images, sound, fonts)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    game.on_keydown(event.key)

        keys = pygame.key.get_pressed()
        game.update(dt, keys)
        game.draw(screen)
        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == '__main__':
    asyncio.run(main())
