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
This module provides the GameDisplay class
"""

from typing import Any

import pygame

from . import settings


class GameDisplay:
    """
    Base class containing the logic of any screen the user may
    interact with, whether it is the gameplay or a menu.
    """
    # exit status values (not an enum, because derived classes
    # will want to add more. Also, no need for numeric values;
    # equality comparison is fully sufficient

    class Status:
        """
        Empty class to define unique status values
        """
        def __init__(self, running: bool = False, **kwargs):
            self.__is_running = running
            self.__data = kwargs

        def is_running(self) -> bool:
            """
            Return True if the status belongs to a running state
            """
            return self.__is_running

        def get(self, key: str) -> Any:
            """
            Get value of extra __init__ argument, or None if nonexistent
            """
            return self.__data.get(key)

    INITIALIZED = Status()
    RUNNING = Status(running = True)
    TERMINATE = Status()
    QUIT = Status()

    EVENT_HIDE_MOUSE = 1


    def __init__(self, media, font):
        """
        Initializes the GameDisplay object
        """
        self.media = media
        self.font = font
        self.status: GameDisplay.Status = self.INITIALIZED

        # key bindings
        self.key_bindings = {
            pygame.K_f: self.media.toggle_fullscreen,
            pygame.K_HASH: self.__screenshot
            }


    def is_running(self):
        """
        Returns true if the current status is a running_state
        """
        return self.status.is_running()


    def draw(self):
        """
        Draws the object.

        To be supplied by the derived class.
        """
        raise NotImplementedError("Must be supplied by the derived class")


    def handle_event(self, event: pygame.event.Event):
        """
        Handle a known event. Returns if the event has been handled.

        This function handles pygame.QUIT, pygame.KEYDOWN,
        pygame.MOUSEMOTION and the user event EVENT_HIDE_MOUSE. To
        handle other events, override this function.
        """
        # A pygame.QUIT event always terminates the game completely
        if event.type == pygame.QUIT:
            self.set_status(self.TERMINATE)
            return True

        if event.type == pygame.KEYDOWN:
            if event.key in self.key_bindings:
                self.key_bindings[event.key]()
                return True

        if event.type == pygame.MOUSEMOTION:
            GameDisplay.__show_mouse_temporarily(
                int(1000*settings.mouse_visibility_time))
            return True

        if event.type == pygame.USEREVENT:
            if event.event == GameDisplay.EVENT_HIDE_MOUSE:
                pygame.mouse.set_visible(False)
                return True

        # If we get here, no event has been handled.
        return False


    def __screenshot(self):
        """
        Make a screenshot of the current display
        """
        pygame.image.save(self.media.get_screen(), settings.screenshot_file)


    # This must be a member function in order to be overridden
    # pylint: disable=no-self-use
    def update_state(self):
        """
        Updates the state.

        Does nothing in the base class. Can, but does not need to be
        overwritten by the derived class.
        """
    # pylint: enable=no-self-use


    def execute(self):
        """
        The main loop
        """
        self.status = self.RUNNING
        while self.is_running():
            self.draw()
            #self.game.clock.tick(self.game.fps)
            self.media.tick()
            for event in pygame.event.get():
                self.handle_event(event)
            self.update_state()
        return self.status


    def set_status(self, status: Status):
        """
        Quit the display, but not necessarily the game
        """
        assert isinstance(status, self.Status)
        self.status = status


    def terminated(self):
        """
        Returns whether quit(TERMINATE) was called.
        """
        return self.status == self.TERMINATE


    # temporarily don't complain about the member not being used
    # pylint: disable=unused-private-member
    @staticmethod
    def __show_mouse_temporarily(time):
        """
        Teporarily show the mouse pointer
        """
        pygame.mouse.set_visible(True)
        event = pygame.event.Event(pygame.USEREVENT,
                                   event=GameDisplay.EVENT_HIDE_MOUSE)
        pygame.time.set_timer(event, time, loops=1)
