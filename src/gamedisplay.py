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

from typing import Union

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

    # This class is intentionally empty, thus make pylint shut up about it
    # pylint: disable=too-few-public-methods
    class Status:
        """
        Empty class to define unique status values
        """
    # pylint: enable=too-few-public-methods

    TERMINATE = Status()
    QUIT = Status()


    def __init__(self, game):
        """
        Initializes the GameDisplay object
        """
        self.game = game
        self.running = False
        self.status: Union[GameDisplay.Status, None] = None

        # key bindings
        self.key_bindings = {
            pygame.K_f: self.game.toggle_fullscreen,
            pygame.K_HASH: self.__screenshot
            }


    def draw(self):
        """
        Draws the object.

        To be supplied by the derived class.
        """
        raise NotImplementedError("Must be supplied by the derived class")


    def handle_event(self, event: pygame.event.Event):
        """
        Handle a known event. Returns if the event has been handled.

        This function handles pygame.QUIT and pygame.KEYDOWN.
        To handle other events, override this function.
        """
        # A pygame.QUIT event always terminates the game completely
        if event.type == pygame.QUIT:
            self.terminate()
            return True

        if event.type == pygame.KEYDOWN:
            if event.key in self.key_bindings:
                self.key_bindings[event.key]()
                return True

        # If we get here, no event has been handled.
        return False


    def __screenshot(self):
        """
        Make a screenshot of the current display
        """
        pygame.image.save(self.game.screen, settings.screenshot_file)


    # This must be a member function in order to be overridden
    # pylint: disable=no-self-use
    def update_state(self):
        """
        Updates the state.

        Does nothing in the base class. Can, but does not need to be
        overwritten by the derived class.
        """
    # pylint: enable=no-self-use


    # This must be a member function in order to be overridden
    # pylint: disable=no-self-use
    def ready_to_quit(self):
        """
        Returns True if the level can actually be quit.

        This method always returns True. It can be overridden by a
        derived class to allow delayed quitting, e.g. to display a
        message.

        When quit() has been called, but this function returns False,
        the event loop still continues, but self.running is false.

        This function is only called from the event loop if
        self.running == False.
        """
        return True
    # pylint: enable=no-self-use


    def execute(self):
        """
        The main loop
        """
        self.running = True
        while self.running or not self.ready_to_quit():
            self.draw()
            self.game.clock.tick(self.game.fps)
            for event in pygame.event.get():
                self.handle_event(event)
            self.update_state()
        return self.status


    def quit(self, status: Status = QUIT):
        """
        Quit the display, but not necessarily the game
        """
        assert isinstance(status, self.Status)
        self.running = False
        self.status = status


    def terminate(self):
        """
        Quit the game
        """
        self.quit(self.TERMINATE)


    def terminated(self):
        """
        Returns whether the terminate function was called.
        """
        return self.status == self.TERMINATE
