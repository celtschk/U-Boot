import pygame

# python files from this game
import settings
import resources
from gamedisplay import DisplayInfo
from menu import Menu
from level import Level

class Game:
    "The game"

    def __init__(self):
        """
        Initialize the game
        """
        pygame.init()

        self.display_info = DisplayInfo(
            screen = pygame.display.set_mode((settings.width,
                                              settings.height)),
            clock = pygame.time.Clock(),
            fps = settings.fps
            )

        pygame.display.set_caption(settings.game_name)
        pygame.mouse.set_visible(False)
        pygame.key.set_repeat(0)

        self.font = pygame.font.SysFont(settings.font["name"],
                                        settings.font["size"])

        # music
        resources.load_music("background")

        self.main_menu = [
            { "text": "Play", "action": "play" },
            { "text": "Options", "action": "options" },
            { "text": "Quit", "action": "quit" }
            ]

        self.options_menu = [
            { "text": "{allow} music", "action": "music" },
            { "text": "Return to main menu", "action": "menu" }
            ]

        self.play_music = True

    def run(self):
        """
        Run the game
        """
        action = "menu"
        while action != "quit":
            if action == "menu" or action == "options":
                if action == "menu":
                    displayed_menu = self.main_menu
                elif action == "options":
                    displayed_menu = self.options_menu
                menu = Menu(self.display_info,
                            displayed_menu,
                            resources.get_colour("menu background"),
                            resources.get_colour("menu option"),
                            resources.get_colour("menu highlight"),
                            self.font,
                            {"allow": ["Enable", "Disable"][self.play_music]})
                menu.execute()
                if menu.terminated():
                    action = "quit"
                else:
                    action = menu.get_selected_action()
            elif action == "music":
                self.play_music = not self.play_music
                action = "options"
            elif action == "play":
                # start the backkground music in infinte loop
                if self.play_music:
                    pygame.mixer.music.play(-1)

                # play the game
                level = Level(self.display_info, self.font)
                level.execute()

                # stop the background music
                if self.play_music:
                    pygame.mixer.music.stop()

                if level.terminated():
                    # quit the game on request
                    action = "quit"
                else:
                    # return to the menu
                    action = "menu"


if __name__=='__main__':
    Game().run()
