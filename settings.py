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

# frames per score animation update
score_frames = 6

# number of frames to show the final message of each level
level_display_frames = 5*fps;

# colours used in the game
colours = {
    "sky": "sky blue",
    "water": "blue",
    "text": "black",
    "pause": "white",
    "cleared": "yellow",
    "failed": "orange",
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
        },
    "whale explosion": {
        "filename": "Torpedo Impact-SoundBible.com-765913562.wav",
        "volume": 1
        },
    "winning": {
        "filename": "Short_triumphal_fanfare-John_Stracke-815794903.wav",
        "volume": 0.5
        },
    "losing": {
        "filename": "Sad_Trombone-Joe_Lamb-665429450.wav",
        "volume": 0.5
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
        "total_count": 50,
        "to_destroy": 30,
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
        "max_count": 15,
        "total_count": 100
        },
    "whale": {
        "filename": "whale.png",
        "origin": (0,0),
        "movement": {
            "start": ("right", "depth"),
            "speed": {
                "min": 0.01,
                "max": 0.05
                },
            "direction": (-1,0),
            "repeat": False
            },
        "max_count": 10,
        "total_count": 50,
        "to_destroy": 30,
        "depth": {
            "min": 0.1,
            "max": 0.97
            },
        "spawn_rate": 1/20 # average spawns per second
        }
    }

# information about possible hits
hit_info = {
    ("submarine", "bomb"): {
        # Which animation to play on hit. Animations are always played
        # at the position of the second object
        "animation": "explosion",

        # Which sound to play on hit.
        "sound": "explosion",

        # Whether a hit results in a score
        "score": True
        },
    ("whale", "bomb"): {
        "animation": "explosion",
        "sound": "whale explosion",
        "score": False
        }
    }

level_updates = {
    1:  {
        "submarine": {
            "depth": {
                "max": 0.2
                }
            },
        "whale": {
            "depth": {
                "min": 0.25
                }
            }
        },
    2:  {
        "submarine": {
            "depth": {
                "max": 0.4
                }
            }
        },
    3:  {
        "submarine": {
            "depth": {
                "max": 0.6
                }
            }
        }
    }

save_file = "uboot.save"
