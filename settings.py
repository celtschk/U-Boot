# Settings for the uboot game

# Name of the game
game_name = "U-Boot"

# screen resolution/window size
width = 1024
height = 768

# fraction of the screen that's sky
sky_fraction = 0.2

# frame rate
fps = 60

# colours used in the game
colours = {
    "sky": "sky blue",
    "water": "blue",
    "text": "black",
    "pause": "white"
    }

# font used in the game
font = {
    "name": "Courier New",
    "size": 30
    }

# sounds used in the game
sounds = {
    "explosion": {
        "filename": "Flashbang-Kibblesbob-899170896.wav",
        "volume": 0.2
        }
    }

music = {
    "background": {
        "filename": "The Enemy.mp3",
        "volume": 0.1
        }
    }

# list of game objects and their properties
objects = {
    "ship": {
        "filename": "schiff.png",
        "speed": 0.1
        },
    "submarine": {
        "filename": "Uboot.png",
        "speed": {
            "min": 0.05,
            "max": 0.2
            },
        "max_count": 10,
        "depth": {
            "min": 0.1,
            "max": 0.97
            },
        "spawn_rate": 1/3 # average spawns per second
        },
    "bomb": {
        "filename": "bomb.png",
        "speed": 0.1,
        "max_count": 15
        }
    }
