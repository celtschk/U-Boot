import settings
import pygame
from dataclasses import dataclass

# get the colour names from X11's rgb.txt
rgbvalues = {}
with open("rgb.txt", "r") as rgbfile:
    for line in rgbfile:
        if line == "" or line[0] == '!':
            continue
        rgb, name = line.split('\t\t')
        rgbvalues[name.strip()] = tuple(int(value) for value in rgb.split())

def get_colour(name):
    """
    Get the rgb values of a named colour.

    The name is looked up in the settings, or failing that, in the rgb
    database. If the settings give a string as colour, that string is
    again looked up, otherwise the result is assumed to be a valid
    colour representation and returned.
    """
    while name in settings.colours:
        colour = settings.colours[name]
        if type(colour) is str:
            name = colour
        else:
            return colour
    return rgbvalues[name]

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
    
