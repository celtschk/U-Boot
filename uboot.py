"""
U-Boot: A simple game
"""

import shelve

import pygame
# work around pylint not understanding pygame
# pylint: disable=no-name-in-module
from pygame import (
    FULLSCREEN as pygame_FULLSCREEN,
    init as pygame_init
    )
# pylint: enable=no-name-in-module

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
        pygame_init()

        self.screen = pygame.display.set_mode((settings.width,
                                               settings.height))
        self.clock = pygame.time.Clock()
        self.fps = settings.fps

        pygame.display.set_caption(settings.game_title)
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
        if self.screen.get_flags() & pygame_FULLSCREEN:
            pygame.display.set_mode(size)
        else:
            pygame.display.set_mode(size, pygame_FULLSCREEN)


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
            if result != Level.LEVEL_CLEARED:
                break
            state = level.get_state()
            level = Level(self, Level.initial_state(state))

        # stop the background music
        if self.options["music"]:
            pygame.mixer.music.stop()

        return result, level.get_state()


    def display_menu(self, menu_name, message):
        """
        Display a menu
        """
        menu = Menu(self,
                    self.menus[menu_name],
                    resources.get_colour("menu background"),
                    resources.get_colour("menu option"),
                    resources.get_colour("menu highlight"),
                    resources.get_colour("menu message"),
                    self.font,
                    message)
        menu.execute()
        if menu.terminated():
            return "quit"
        return menu.get_selected_action()


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
                # show help
                with open("helptext.txt", encoding="utf8") as helpfile:
                    helptext = helpfile.read()

                helpscreen = TextScreen(self, helptext)
                helpscreen.execute()

                if helpscreen.terminated():
                    action = "quit"
                else:
                    action = "menu"
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

                    if result == Level.TERMINATE:
                        # quit the game on request
                        action = "quit"
                    else:
                        # return to the menu
                        action = "menu"


if __name__=='__main__':
    Game().run()
