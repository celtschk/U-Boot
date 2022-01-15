import pygame
import shelve

# python files from this game
import settings
import resources
from menu import Menu
from level import Level

class Game:
    "The game"

    def __init__(self):
        """
        Initialize the game
        """
        pygame.init()

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

        # music
        resources.load_music("background")

        main_menu = [
            { "text": "Play new game", "action": "play" },
            { "text": "Resume saved game", "action": "resume" },
            { "text": "Options", "action": "options" },
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
                else:
                    return "Disabled"
            return value;

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
            settings.debug["level"] = level

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


    def display_menu(self, menu_name):
        menu = Menu(self,
                    self.menus[menu_name],
                    resources.get_colour("menu background"),
                    resources.get_colour("menu option"),
                    resources.get_colour("menu highlight"),
                    self.font)
        menu.execute()
        if menu.terminated():
            return "quit"
        else:
            return menu.get_selected_action()


    def run(self):
        """
        Run the game
        """
        action = "menu"
        while action != "quit":
            if action in self.menus.keys():
                action = self.display_menu(action)
            elif action == "play" or action == "resume":
                # play the game
                if action == "play":
                    state = Level.initial_state()
                elif action == "resume":
                    save_file = resources.get_save_file()
                    with shelve.open(str(save_file)) as savefile:
                        state = savefile["game"]

                result, state = self.play(state)

                if result == Level.LEVEL_SAVE:
                    save_file = resources.get_save_file()
                    with shelve.open(str(save_file), "c") as savefile:
                        savefile["game"] = state

                if result == Level.TERMINATE:
                    # quit the game on request
                    action = "quit"
                else:
                    # return to the menu
                    action = "menu"


if __name__=='__main__':
    Game().run()
