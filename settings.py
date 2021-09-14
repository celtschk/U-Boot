# Settings for the uboot game

# Name of the game
game_name = "U-Boot"

# screen resolution/window size
width = 1024
height = 768

# fraction of the screen that's sky
sky_fraction = 0.2

# file names of the game graphics
image_files = {
    "ship": "schiff.png",
    "submarine": "Uboot.png",
    "bomb": "bomb.png"
    }

# frame rate
fps = 60

# speeds of objects
speeds = {
    "ship": 0.1,
    "submarine_min": 0.05,
    "submarine_max": 0.2,
    "bomb": 0.1
    }

# maximum number of objects
limits = {
    "submarine": 10,
    "bomb": 15
    }

# spawn rate (in average spawns per second) of randomly spawned obcets
# (currently only submarines)
spawn_rates = {
    "submarine": 1/3
    }

# colours used in the game
colours = {
    "sky": "sky blue",
    "water": "blue",
    "text": "black"
    }

# font used in the game
font = {
    "name": "Courier New",
    "size": 30
    }
