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
This module provides menus for the game
"""

from functools import partial

import pygame

from . import resources
from .gamedisplay import GameDisplay


class Menu(GameDisplay):
    """
    Class representing a menu.
    """

    MENU_MAIN = GameDisplay.Status()

    def __init__(self, game, menuspec, font, message = None):
        """
        Initialize the menu
        """
        super().__init__(game)
        self.menuspec = menuspec
        self.colours = {
            "background": resources.get_colour("menu background"),
            "option":     resources.get_colour("menu option"),
            "highlight":  resources.get_colour("menu highlight"),
            "message":    resources.get_colour("menu message")
            }
        self.font = font
        self.selection = 0
        self.message = message

        # menu specific keybindings
        self.key_bindings.update({
            pygame.K_UP: self.__move_up,
            pygame.K_DOWN: self.__move_down,
            pygame.K_RETURN: self.__select_option,
            pygame.K_q: partial(self.quit, Menu.MENU_MAIN),
            pygame.K_ESCAPE: partial(self.quit, Menu.MENU_MAIN)
            })


    def draw(self):
        """
        Draw the menu
        """
        screen = self.game.screen
        screen.fill(self.colours["background"])

        line_height = 50
        center_x = screen.get_width()//2
        center_y = screen.get_height()//2

        current_line = center_y - (len(self.menuspec)-1)*line_height/2

        for index, option in enumerate(self.menuspec):
            if index == self.selection:
                colour = self.colours["highlight"]
            else:
                colour = self.colours["option"]

            values = option.get("values", {})

            params = { key: fn() for key, fn in values.items() }

            text = resources.MessageData(
                message = option["text"].format(**params),
                position = (center_x, current_line),
                colour = colour,
                font = self.font,
                origin = (0.5,0.5) # centered
                )

            text.write(screen)

            current_line += line_height

        if self.message is not None:
            current_line += line_height

            text = resources.MessageData(
                message = self.message,
                position = (center_x, current_line),
                colour = self.colours["message"],
                font = self.font,
                origin = (0.5, 0.5)
                )

            text.write(screen)

        pygame.display.flip()


    def __move_up(self):
        """
        Move the menu selection one position up
        """
        if self.selection == 0:
            self.selection = len(self.menuspec)
        self.selection -= 1


    def __move_down(self):
        """
        Move the menu selection one position down
        """
        self.selection += 1
        if self.selection == len(self.menuspec):
            self.selection = 0


    def __select_option(self):
        """
        Select a menu option
        """
        action = self.menuspec[self.selection]["action"]
        if isinstance(action, str):
            self.quit()
        else:
            action()


    def handle_event(self, event):
        """
        Make any message disappear on pressing a key
        """
        if event.type == pygame.KEYDOWN:
            # If there's a message, any keypress makes it disappear
            self.message = None

        if super().handle_event(event):
            return True

        return False


    def get_selected_action(self):
        """
        Get the selected action, or None if a pygame.QUIT event was
        received
        """
        if self.terminated():
            return None
        if self.status == Menu.MENU_MAIN:
            return "menu"
        return self.menuspec[self.selection]["action"]
