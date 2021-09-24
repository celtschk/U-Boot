# Settings for the uboot game

# Name of the game
game_name = "uboot"
game_title = "U-Boot"
game_version = "0.1"
game_author = "celtschk"

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
    "pause": "white",
    "menu background": "dark blue",
    "menu option": "white",
    "menu highlight": "red"
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

# animations used in the game
animations = {
    "explosion": {
        # frame rate of the animation
        # for best results, use a factor of the global fps
        "fps": 10,

        # total number of frames in the animation
        "frame_count": 5,
        
        # image file name format string, with the frame number
        # replaced by {frame}. The first
        "images": "explosion_{frame}.png"
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
        "origin": (0.5,1),
        "movement": {
            "start": ("left", 0),
            "speed": 0.1,
            "direction": (1,0),
            "repeat": True
            },
        },
    "submarine": {
        "filename": "Uboot.png",
        "origin": (0, 0),
        "movement": {
            "start": ("right", "depth"),
            "speed": {
                "min": 0.05,
                "max": 0.2
                },
            "direction": (-1,0),
            "repeat": False
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
        "origin": (0.5, 0),
        "movement": {
            "start": ("ship", "ship"),
            "speed": 0.1,
            "direction": (0,1),
            "repeat": False
            },
        "max_count": 15
        }
    }

save_file = "uboot.save"
#save_file = "/home/ce/test/savefile.shelve"
