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
This module provides a class managing all the media the game interacts
with (here the clock also is considered a medium).
"""

import pygame

from . import resources

class Media:
    """
    Collectively handle all media
    """
    def __init__(self, title: str, width: int, height: int, fps: int) -> None:
        self.__dimensions = (width, height)
        self.__fps = fps

        self.__music_loaded = False
        self.__music_enabled = False
        self.__sound_enabled = True

        pygame.init()

        pygame.mouse.set_visible(False)
        pygame.key.set_repeat(0)

        self.__screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)

        self.clock = pygame.time.Clock()


    def load_music(self, title: str) -> None:
        """
        Load music to play
        """
        resources.load_music(title)
        self.__music_loaded = True


    def enable_music(self, enable : bool = True) -> None:
        """
        Enable/Disable playing music
        """
        self.__music_enabled = enable and self.__music_loaded


    def play_music(self):
        """
        If music is enabled, play it in a loop
        """
        if self.__music_enabled:
            pygame.mixer.music.play(-1)


    def stop_music(self):
        """
        If music is enabled, stop it
        """
        if self.__music_enabled:
            pygame.mixer.music.stop()


    def pause_music(self):
        """
        If music is enabled, pause it
        """
        if self.__music_enabled:
            pygame.mixer.music.pause()


    def unpause_music(self):
        """
        If music is enabled, unpause it
        """
        if self.__music_enabled:
            pygame.mixer.music.unpause()


    def enable_sound(self, enable: bool = True) -> None:
        """
        Enable/Disable playing sounds
        """
        self.__sound_enabled = enable


    def play_sound(self, sound_name: str) -> None:
        """
        Play a sound if sound playing is enabled
        """
        if self.__sound_enabled:
            sound = resources.get_sound(sound_name)
            sound.play()


    def toggle_fullscreen(self):
        """
        toggle between fullscreen and windowed
        """
        size = self.__dimensions
        if self.__screen.get_flags() & pygame.FULLSCREEN:
            pygame.display.set_mode(size)
        else:
            pygame.display.set_mode(size, pygame.FULLSCREEN)


    def get_screen(self):
        """
        Get the screen
        """
        return self.__screen


    def get_dimensions(self):
        """
        Get the screen dimensions
        """
        return self.__dimensions


    def get_fps(self):
        """
        Return the frames per second
        """
        return self.__fps


    def tick(self):
        """
        Tick the clock
        """
        self.clock.tick(self.__fps)


    def get_time(self):
        """
        Get clock time in seconds
        """
        return self.clock.get_time()/1000
