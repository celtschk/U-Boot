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
This module provides access to various resources.
"""

import random
import pathlib
from dataclasses import dataclass

import pygame
import appdirs

import settings

# A storage for images, so that they aren't loaded each time
# another object uses the same image is
imagestore = {}


def load_image(path):
    """
    Load an image, if not already loaded. Otherwise, return the
    already loaded image.
    """
    if not path in imagestore:
        imagestore[path] = pygame.image.load(path).convert_alpha()
    return imagestore[path]


def subset_or_none(dict1, dict2):
    """
    If the keys of dict2 are a subset of the keys of dict1,
    return a copy of dict1 updated with the values of dict2,
    otherwise return an empty dict of the same type as dict1
    """
    new_dict = dict1.copy()
    new_dict.update(dict2)
    if new_dict.keys() == dict1.keys():
        return dict1.__class__(new_dict)
    return dict1.__class__()


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

    # ------------------------------------------------------------
    # the main function code of get_colour
    previous_names = { name }

    while name in settings.colours:
        colour = settings.colours[name]

        if isinstance(colour, str):
            # prevent endless loop
            if colour in previous_names:
                raise ValueError("recursive colour specification")
            previous_names.add(colour)
            name = colour

        elif isinstance(colour, int):
            return pygame.Color(colour, colour, colour)

        elif isinstance(colour, tuple):
            return pygame.Color(*colour)

        elif isinstance(colour, dict):
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


sound_store = {}

def get_sound(sound_name):
    """
    Get a pygame sound from a sound name.

    This looks up the sound information in the settings file and
    returns a pygame Sound object created from the data found there
    """
    if sound_name in sound_store:
        sound = sound_store[sound_name]
    else:
        sound_info = settings.sounds[sound_name]
        sound = pygame.mixer.Sound(sound_info["filename"])
        sound.set_volume(sound_info["volume"])
        sound_store[sound_name] = sound
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
    """
    This class represents a message to be displayed on the screen
    """
    message: str
    position: tuple
    colour: tuple
    font: pygame.font.SysFont
    origin: tuple = (0, 0)
    cache: tuple = (None, None)


    # The argument data is not changed in the function, therefore the
    # default value is safe
    # pylint: disable=dangerous-default-value
    def write(self, screen, data = {}):
        """
        Write the message at a given position on screen
        """
        string = self.message.format(**data)

        # avoid re-rendering if the text didn't change
        if string == self.cache[0]:
            text = self.cache[1]
        else:
            if callable(self.colour):
                # pylint: disable=not-callable
                colour = self.colour(data)
                # pylint: enable=not-callable
            else:
                colour = self.colour
            text = self.font.render(string, True, colour)
            self.cache = (string, text)

        textsize = (text.get_width(), text.get_height())
        position = tuple(int(pos - size * orig)
                         for pos, size, orig
                         in zip(self.position,
                                textsize,
                                self.origin))

        screen.blit(text, position)
    # pylint: enable=dangerous-default-value


def get_value(value_or_range):
    """
    Get a specific or random value from a given specification.

    The specification can either be the value itself, or an interval
    given through a dictionary with the entries \"min\" and \"max\"
    specifying respectively the minimal and maximal value of the
    interval to uniformly choose from.
    """
    if isinstance(value_or_range, dict):
        return random.uniform(value_or_range["min"],
                              value_or_range["max"])
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
        appname = settings.game_info["name"],
        appauthor = settings.game_info["author"],
        version = settings.game_info["version"]
        ))

    # ensure the directory exists
    user_data_dir.mkdir(parents=True, exist_ok=True)

    return user_data_dir/settings.save_file


def try_load_all():
    """
    This function tries to load all resources that will be used in the
    game, so that errors can be caught right away rather than in the
    middle of the game.
    """

    # load all the images for objects
    for obj in settings.objects.values():
        load_image(obj["filename"])

    # load all the images for animations
    for animation in settings.animations.values():
        for frame_number in range(animation["frame_count"]):
            load_image(animation["images"].format(frame=frame_number))

    # load all the sounds
    for sound in settings.sounds:
        get_sound(sound)

    # load all the music
    for music in settings.music:
        load_music(music)

    # try to resolve all colours
    for colour in settings.colours:
        get_colour(colour)


def recursive_update(dictionary, updates):
    """
    Recursively update a dictionary.
    """
    for key, value in updates.items():
        if key in dictionary:
            oldvalue = dictionary[key]
            if value is None:
                del dictionary[key]
            elif isinstance(value, dict) and isinstance(oldvalue, dict):
                recursive_update(oldvalue, value)
            else:
                dictionary[key] = value


def bisect(first, last, condition):
    """
    Returns the largest integer i with first <= i <= last such that
    condition(i-1) is True.

    Requires truth of condition(first) and that condition(i+1)
    implies condition(i).
    """
    left, right = first, last
    while left + 1 < right:
        middle = (left + right) // 2
        if condition(middle):
            left = middle
        else:
            right = middle

    return right
