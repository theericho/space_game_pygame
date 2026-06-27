"""
Constants for Space Invaders

All coordinates are in pixels. The origin is the TOP-left corner and the y axis
points DOWN, so positions here are written in screen coordinates (small y = top
of the window).
"""

### WINDOW CONSTANTS (all coordinates are in pixels) ###

# the width of the game display
GAME_WIDTH  = 800
# the height of the game display
GAME_HEIGHT = 700
# the number of animation frames per second
FPS = 60


### SHIP CONSTANTS ###

# the width of the ship
SHIP_WIDTH    = 44
# the height of the ship
SHIP_HEIGHT   = 44
# the distance of the (bottom of the) ship from the bottom of the window
SHIP_BOTTOM   = 32
# the number of pixels to move the ship per frame
SHIP_MOVEMENT = 5
# the number of lives a ship has
SHIP_LIVES    = 3


# the y-coordinate of the defensive line, measured from the bottom of the window
DEFENSE_LINE = 100


### ALIEN CONSTANTS ###

# the width of an alien
ALIEN_WIDTH   = 33
# the height of an alien
ALIEN_HEIGHT  = 33
# the horizontal separation between aliens
ALIEN_H_SEP   = 16
# the vertical separation between aliens
ALIEN_V_SEP   = 16
# the number of horizontal pixels to move an alien
ALIEN_H_WALK  = ALIEN_WIDTH // 4
# the number of vertical pixels to move an alien
ALIEN_V_WALK  = ALIEN_HEIGHT // 2
# the distance of the top alien from the top of the window
ALIEN_CEILING = 100
# the number of rows of aliens
ALIEN_ROWS    = 5
# the number of aliens per row
ALIENS_IN_ROW = 12
# the image files for the aliens (bottom to top)
ALIEN_IMAGES  = ('alien1.png', 'alien2.png', 'alien3.png')
# the number of seconds (0 < float <= 1) between alien steps
ALIEN_SPEED   = 1.0
# the number of seconds to decrease between alien steps w/ each new wave
ALIEN_SP_DEC  = 0.05
# the increment in speed, multiplied to wavespeed with each alien killed
INCREMENT     = 0.985


### BOLT CONSTANTS ###

# the width of a laser bolt
BOLT_WIDTH  = 4
# the height of a laser bolt
BOLT_HEIGHT = 16
# the number of pixels to move the bolt per frame
BOLT_SPEED  = 10
# the number of alien steps (not frames) between alien bolts
BOLT_RATE   = 8


### GAME STATE CONSTANTS ###

# state before the game has started (start screen)
STATE_INACTIVE    = 0
# state when we are initializing a new wave (one frame)
STATE_NEWWAVE     = 1
# state when the wave is activated and in play
STATE_ACTIVE      = 2
# state when we are paused between lives (press S to continue)
STATE_PAUSED      = 3
# state when we are restoring a destroyed ship (one frame)
STATE_CONTINUE    = 4
# state when the game is complete (won or lost)
STATE_COMPLETE    = 5
# state when the player manually paused the game with 'p'
STATE_MANUALPAUSE = 6


### COLOR CONSTANTS ###

# the background color
COLOR_BG    = (0, 0, 0)
# the color of the defensive line
COLOR_LINE  = (40, 80, 214)
# the color of a player bolt
COLOR_PBOLT = (255, 0, 0)
# the color of an alien bolt
COLOR_ABOLT = (0, 80, 255)
# the color of the centered messages
COLOR_TEXT  = (255, 200, 0)
# the color of the heads-up display text
COLOR_HUD   = (255, 255, 255)
