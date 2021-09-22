import pygame
import random
import appdirs
import pathlib
from dataclasses import dataclass

import settings

def subset_or_none(d1, d2):
    """
    If the keys of d2 are a subset of the keys of d1,
    return a copy of d1 updated with the values of d2,
    otherwise return an empty dict of the same type as d1
    """
    d = d1.copy()
    d.update(d2)
    if d.keys() == d1.keys():
        return d
    else:
        return d.__class__()


# Helper functions to create pygame.Color objects
# these are used because pygame.Color does not support named
# arguments for the colours, and furthermore some colour models
# are only available through direct assignment of properties
def rgb(red, green, blue):
    """
    Returns a Color object with the specified rgb values
    """
    return pygame.Color(red, green, blue)


def greyscale(grey):
    """
    Returns a Color object corresponding to zjr specified grey value
    """
    return pygame.Color(grey, grey, grey)


# This function is separate from greyscale because of the different
# argument name
def grayscale(gray):
    """
    Returns a Color object corresponding to zjr specified grey value
    """
    return pygame.Color(gray, gray, gray)


def hsv(hue, saturation, value):
    """
    Returns a Color object with the specified hsv values
    """
    colour = pygame.Color(0)
    colour.hsva = (hue, saturation, value, 100)
    return colour


def hsl(hue, saturation, lightness):
    """
    Returns a Color object with the specified hsl values
    """
    colour = pygame.Color(0)
    colour.hsla = (hue, saturation, lightness, 100)
    return colour


def get_colour(name):
    """
    Get the rgb values of a named colour.

    The name is looked up in the settings. If the settings give a
    string as colour, that string is again looked up. Otherwise, it is
    passed to pygame.Color as follows:

      * If it is an integer, it is passed as red, green, blue,
        making it a grey level.

      * If it is a tuple, it is interpolated to pygame.Color, thus it
        must be a valid argument list. With color names, this can be
        used to bypass further name lookup. It also is the only way to
        get an alpha value (because of pygame's inconsistent ranges
        for alpha values in different colour models this option is
        omitted otherwise)

      * If it is a dictionary, the following key sets are recognized;
        the first set that fits is chosen. If a key is missing, the
        specified default value is used.

          * { "red": 0, "green": 0, "blue": 0 }

            If some, but not all are present, the remaining ones are
            set to zero (red, green, blue). The values have to be in
            the range [0, 255].

          * { "grey": 0 } or { "gray": 0 }

            Those two are equivalent. { "grey": value } is equivalent
            to { "red": value, "green": value, "blue": value }.
            The value has to be in the range [0,255].

          * { "hue": 0, "saturation": 100, "value": 100 }

            This uses the pygame hsv implementation.

          * { "hue": 0 , "saturation": 100, "lightness": 50 }

            This uses the pygame hsl implementation. Actually
            because of being preceded by hsv, the lightness
            default value is inaccessible.
    """
    previous_names = { name }

    while name in settings.colours:
        colour = settings.colours[name]

        if type(colour) is str:
            # prevent endless loop
            if colour in previous_names:
                raise ValueError("recursive colour specification")
            previous_names.add(colour)
            name = colour

        elif type(colour) is int:
            return pygame.Color(colour, colour, colour)

        elif type(colour) is tuple:
            return pygame.Color(*colour)

        elif type(colour) is dict:
            colour_options = [
                ({"red": 0, "green": 0, "blue": 0}, rgb),
                ({"grey": 0}, greyscale),
                ({"gray": 0}, grayscale),
                ({"hue": 0, "saturation": 100, "value": 100}, hsv),
                ({"hue": 0, "saturation": 100, "lightness": 50}, hsl)
                ]

            for model, function in colour_options:
                full_colour = subset_or_none(model, colour)
                if full_colour:
                    return function(**full_colour)

            raise ValueError("invalid colour specification")

    return pygame.Color(name)


def get_sound(sound_name):
    """
    Get a pygame sound from a sound name.

    This looks up the sound information in the settings file and
    returns a pygame Sound object created from the data found there
    """
    sound_info = settings.sounds[sound_name]
    sound = pygame.mixer.Sound(sound_info["filename"])
    sound.set_volume(sound_info["volume"])
    return sound


def load_music(music_name):
    """
    Sets up pygame music from a music name.

    This looks up the sound information in the settings file and sets
    up the music to play in the background, but doesn't actually start
    playing.
    """
    music_info = settings.music[music_name]
    pygame.mixer.music.load(music_info["filename"])
    pygame.mixer.music.set_volume(music_info["volume"])



@dataclass
class MessageData:
    message: str
    position: tuple
    colour: tuple
    font: pygame.font.SysFont
    origin: tuple = (0, 0)


    def write(self, screen, data = {}):
        """
        Write the message at a given position on screen
        """
        string = self.message.format(**data)

        text = self.font.render(string, True, self.colour)
        textsize = (text.get_width(), text.get_height())
        position = tuple(int(pos - size * orig)
                         for pos, size, orig
                         in zip(self.position,
                                textsize,
                                self.origin))

        screen.blit(text, position)


def get_value(value_or_range):
    """
    Get a specific or random value from a given specification.

    The specification can either be the value itself, or an interval
    given through a dictionary with the entries \"min\" and \"max\"
    specifying respectively the minimal and maximal value of the
    interval to uniformly choose from.
    """
    if type(value_or_range) is dict:
        return random.uniform(value_or_range["min"],
                              value_or_range["max"])
    else:
        return value_or_range


def randomly_true(probability):
    """
    Return True with a given probability, False otherwise.
    """
    return random.uniform(0,1) < probability


def get_save_file():
    """
    Get the name of the game save file
    """
    user_data_dir = pathlib.Path(appdirs.user_data_dir(
        appname = settings.game_name,
        appauthor = settings.game_author,
        version = settings.game_version
        ))

    # ensure the directory exists
    user_data_dir.mkdir(parents=True, exist_ok=True)

    return user_data_dir/settings.save_file
