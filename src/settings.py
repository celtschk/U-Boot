#  Copyright 2022 Christopher Eltschka
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""
Settings for the uboot game
"""

# pylint: disable=invalid-name

# Information about the game
game_info = {
    "name": "uboot",
    "title": "U-Boot",
    "version": "0.1",
    "author": "celtschk"
    }

# Game geometry data
geometry = {
    # screen resolution/window size
    "width": 1024,
    "height": 768,

    # fraction of the screen that's sky
    "sky_fraction": 0.2
    }

# frame rate
fps = 60

# frames per score animation update
score_frames = 6

# number of frames to show the final message of each level
level_display_frames = 5*fps

# how many seconds transient displays stay
transient_display_time = 3

# the number of lives
lives = 4

# colours used in the game
colours = {
    # background colours
    "sky": "sky blue",
    "water": "blue",

    # game text colours
    "text": "black",
    "pause": "white",
    "cleared": "yellow",
    "failed": "orange",
    "good news": "dark green",
    "bad news": "red",
    "no bombs": "bad news",
    "no more subs to destroy": "good news",
    "not enough subs": "bad news",
    "score delta": "green",
    "bomb score delta": "bad news",

    # menu colours
    "menu background": "dark blue",
    "menu option": "white",
    "menu highlight": "red",
    "menu message": "orange",

    # paginated text colours
    "paginated text": "white",
    "paginated background": "blue",
    "paginated footer": "orange",
    "invalid control sequence": "red",

    # bubbles
    "bubble interior": { "hue": 240, "lightness": 70 },
    "bubble boundary": "dark blue"
    }

# font used in the game
font = {
    "name": "Courier New",
    "size": 30
    }

# font used for paginated text
paginated_font = {
    "name": "Courier New", # "Helvetica",
    "size": 30
    }

# layout of paginated text (all sizes are in pixels)
paginate_layout = {
    "border": {
        "top": 50,
        "left": 70,
        "right": 70,
        "bottom": 50
        },
    "line spacing": 30
    }

# sounds used in the game
sounds = {
    "explosion": {
        "filename": "assets/Flashbang-Kibblesbob-899170896.wav",
        "volume": 0.2
        },
    "whale explosion": {
        "filename": "assets/Torpedo Impact-SoundBible.com-765913562.wav",
        "volume": 1
        },
    "winning": {
        "filename": "assets/Short_triumphal_fanfare-John_Stracke-815794903.wav",
        "volume": 0.5
        },
    "losing": {
        "filename": "assets/Sad_Trombone-Joe_Lamb-665429450.wav",
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
        "images": "assets/explosion_{frame}.png"
        }
    }

music = {
    "background": {
        "filename": "assets/The Enemy.mp3",
        "volume": 0.1
        }
    }

# list of game objects and their properties
objects = {
    "ship": {
        "filename": "assets/schiff.png",
        "origin": (0.5,1),
        "movement": {
            "start": ("left", 0),
            "speed": 0.1,
            "direction": (1,0),
            "area": "sky",
            "repeat": True
            },
        },
    "bubble": {
        "function": "bubble",
        "origin": (0, 1), # (0.5, 0.5),
        "size": {
            "min": 1,
            "max": 5
            },
        "movement": {
            "start": ("startx", "startdepth"),
            "speed": {
                "min": 0.01,
                "max": 0.1
                },
            "direction": (0,-1),
            "area": "water",
            "repeat": False
            },
        "constants": {
            "startx": {
                "min": 0,
                "max": geometry["width"]
                },
            "startdepth": {
                "min": 0.2,
                "max": 1
                }
            },
        "max_count": 20,
        "total_count": 1000, # basically unlimited
        "spawn_rate": 1
        },
    "submarine": {
        "filename": "assets/Uboot.png",
        "origin": (0, 0),
        "movement": {
            "start": ("right", "depth"),
            "speed": {
                "min": 0.05,
                "max": 0.2
                },
            "direction": (-1,0),
            "area": "water",
            "repeat": False
            },
        "max_count": 10,
        "total_count": 50,
        "to_destroy": 30,
        "constants": {
            "depth": {
                "min": 0.1,
                "max": 0.97
                }
            },
        "spawn_rate": 1/3 # average spawns per second
        },
    "bomb": {
        "filename": "assets/bomb.png",
        "origin": (0.5, 0),
        "movement": {
            "start": ("ship", "ship"),
            "speed": 0.1,
            "direction": (0,1),
            "area": "water",
            "repeat": False
            },
        "max_count": 15,
        "total_count": 100
        },
    "whale": {
        "filename": "assets/whale.png",
        "origin": (0,0),
        "movement": {
            "start": ("right", "depth"),
            "speed": {
                "min": 0.01,
                "max": 0.05
                },
            "direction": (-1,0),
            "area": "water",
            "repeat": False
            },
        "max_count": 10,
        "total_count": 50,
        "to_destroy": 30,
        "constants": {
            "depth": {
                "min": 0.1,
                "max": 0.97
                }
            },
        "spawn_rate": 1/20 # average spawns per second
        },
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
            "constants": {
                "depth": {
                    "max": 0.2
                    }
                }
            },
        "whale": {
            "constants": {
                "depth": {
                    "min": 0.25
                    }
                }
            }
        },
    2:  {
        "submarine": {
            "constants": {
                "depth": {
                    "max": 0.4
                    }
                }
            }
        },
    3:  {
        "submarine": {
            "constants": {
                "depth": {
                    "max": 0.6
                    }
                }
            }
        }
    }

save_file = "uboot.save"
screenshot_file = "U-Boot-screenshot.png"
