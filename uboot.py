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
U-Boot: A simple game
"""

import shelve

import pygame

# python files from this game
import settings
import resources
from menu import Menu
from level import Level
from textscreen import TextScreen

class Game:
    "The game"

    def __init__(self):
        """
        Initialize the game
        """
        pygame.init()

        self.screen = pygame.display.set_mode((settings.geometry["width"],
                                               settings.geometry["height"]))
        self.clock = pygame.time.Clock()
        self.fps = settings.fps

        pygame.display.set_caption(settings.game_info["title"])
        pygame.mouse.set_visible(False)
        pygame.key.set_repeat(0)

        # try to load all resources, for early failing
        resources.try_load_all()

        self.font = pygame.font.SysFont(settings.font["name"],
                                        settings.font["size"])

        self.paginated_font = pygame.font.SysFont(
            settings.paginated_font["name"],
            settings.paginated_font["size"])

        # music
        resources.load_music("background")

        main_menu = [
            { "text": "Play new game", "action": "play" },
            { "text": "Resume saved game", "action": "resume" },
            { "text": "Options", "action": "options" },
            { "text": "Help", "action": "help" },
            { "text": "Quit", "action": "quit" }
            ]

        self.options = {
            "music": True,
            "sound": True
            }

        def toggle(option):
            def do_it():
                self.options[option] = not self.options[option]
            return do_it

        def text_enabled(option):
            def value():
                if self.options[option]:
                    return "Enabled"
                return "Disabled"
            return value

        options_menu = [
            {
                "text": "Music: {allow_music}",
                "action": toggle("music"),
                "values": {
                    "allow_music": text_enabled("music")
                    }
                },
            {
                "text": "Sound effects: {allow_sound}",
                "action": toggle("sound"),
                "values": {
                    "allow_sound": text_enabled("sound")
                    }
                },
            {
                "text": "Return to main menu",
                "action": "menu"
                }
            ]

        self.menus = {
            "menu": main_menu,
            "options": options_menu
            }


    def toggle_fullscreen(self):
        """
        toggle between fullscreen and windowed
        """
        size = (self.screen.get_width(), self.screen.get_height())
        if self.screen.get_flags() & pygame.FULLSCREEN:
            pygame.display.set_mode(size)
        else:
            pygame.display.set_mode(size, pygame.FULLSCREEN)


    def play(self, state):
        """
        Actually play the game
        """
        # start the backkground music in infinte loop
        if self.options["music"]:
            pygame.mixer.music.play(-1)

        level = Level(self, state)

        if "debug" in settings.__dict__:
            # pylint: disable=no-member
            settings.debug["level"] = level
            # pylint: enable=no-member

        while True:
            pygame.mixer.music.unpause()
            result = level.execute()
            if result == Level.LEVEL_CLEARED:
                repeat = False
            elif result == Level.LEVEL_FAILED and state["lives"] > 1:
                repeat = True
            else:
                break
            state = level.get_state()
            level = Level(self, Level.initial_state(state, repeat))

        # stop the background music
        if self.options["music"]:
            pygame.mixer.music.stop()

        return result, level.get_state()


    def display_menu(self, menu_name, message):
        """
        Display a menu
        """
        menu = Menu(self, self.menus[menu_name], self.font, message)
        menu.execute()
        if menu.terminated():
            return "quit"
        return menu.get_selected_action()


    def show_help(self):
        """
        Show help
        """
        with open("helptext.txt", encoding="utf8") as helpfile:
            helptext = helpfile.read()

            helpscreen = TextScreen(self, helptext)
            helpscreen.execute()

            if helpscreen.terminated():
                action = "quit"
            else:
                action = "menu"

            return action


    def run(self):
        """
        Run the game
        """
        action = "menu"
        message = None
        while action != "quit":
            if action in self.menus:
                action = self.display_menu(action, message)
                message = None
            elif action == "help":
                action = self.show_help()
            elif action in ("play", "resume"):
                # play the game
                if action == "play":
                    state = Level.initial_state({})
                elif action == "resume":
                    save_file = resources.get_save_file()
                    with shelve.open(str(save_file)) as savefile:
                        state = savefile.get("game", None)

                if state is None:
                    message = "Did not find saved game"
                    action = "menu"
                else:
                    result, state = self.play(state)

                    if result == Level.LEVEL_SAVE:
                        save_file = resources.get_save_file()
                        with shelve.open(str(save_file), "c") as savefile:
                            savefile["game"] = state
                        message = "Game saved"

                    # the else branch of this must be executed also if
                    # result == Level.LEVEL_SAVE, therefore this must
                    # not be an elif
                    if result == Level.TERMINATE:
                        # quit the game on request
                        action = "quit"

                    else:
                        # return to the menu
                        action = "menu"


if __name__=='__main__':
    Game().run()
