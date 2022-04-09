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

    INITIALIZED = Status()
    RUNNING = Status()
    TERMINATE = Status()
    QUIT = Status()

    EVENT_HIDE_MOUSE = 1


    def __init__(self, game):
        """
        Initializes the GameDisplay object
        """
        self.game = game
        self.status: GameDisplay.Status = self.INITIALIZED

        # set of status values that are considered running (that is,
        # the program should stay in the main loop). Derived classes
        # can add their own values.
        self.running_statuses = { self.RUNNING }

        # key bindings
        self.key_bindings = {
            pygame.K_f: self.game.toggle_fullscreen,
            pygame.K_HASH: self.__screenshot
            }


    def is_running(self):
        """
        Returns true if the current status is a running_state
        """
        return self.status in self.running_statuses


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
            self.quit(self.TERMINATE)
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
        self.status = self.RUNNING
        while self.is_running() or not self.ready_to_quit():
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
