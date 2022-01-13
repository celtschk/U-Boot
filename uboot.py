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

        self.main_menu = [
            { "text": "Play new game", "action": "play" },
            { "text": "Resume saved game", "action": "resume" },
            { "text": "Options", "action": "options" },
            { "text": "Quit", "action": "quit" }
            ]

        self.options_menu = [
            { "text": "{allow_music} music", "action": "music" },
            { "text": "{allow_sound} sound effects", "action": "sound" },
            { "text": "Return to main menu", "action": "menu" }
            ]

        self.play_music = True
        self.play_sound = True


    def toggle_fullscreen(self):
        """
        toggle between fullscreen and windowed
        """
        size = (self.screen.get_width(), self.screen.get_height())
        if self.screen.get_flags() & pygame.FULLSCREEN:
            pygame.display.set_mode(size)
        else:
            pygame.display.set_mode(size, pygame.FULLSCREEN)


    def run(self):
        """
        Run the game
        """
        action = "menu"
        highlight_option = 0
        while action != "quit":
            if action == "menu" or action == "options":
                if action == "menu":
                    displayed_menu = self.main_menu
                elif action == "options":
                    displayed_menu = self.options_menu
                menu = Menu(self,
                            displayed_menu,
                            highlight_option,
                            resources.get_colour("menu background"),
                            resources.get_colour("menu option"),
                            resources.get_colour("menu highlight"),
                            self.font,
                            {"allow_music":
                                 ["Enable", "Disable"][self.play_music],
                             "allow_sound":
                                 ["Enable", "Disable"][self.play_sound]})
                menu.execute()
                if menu.terminated():
                    action = "quit"
                else:
                    action = menu.get_selected_action()
                    highlight_option = 0
            elif action == "music":
                self.play_music = not self.play_music
                action = "options"
                highlight_option = 0
            elif action == "sound":
                self.play_sound = not self.play_sound
                action = "options"
                highlight_option = 1
            elif action == "play" or action == "resume":
                # start the backkground music in infinte loop
                if self.play_music:
                    pygame.mixer.music.play(-1)

                # play the game
                if action == "play":
                    #self.score = 0
                    level = Level(self, Level.initial_state())
                elif action == "resume":
                    save_file = resources.get_save_file()
                    with shelve.open(str(save_file)) as savefile:
                        save_state = savefile["game"]
                        #self.score = save_state["score"]
                        level = Level(self, save_state)

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
                if self.play_music:
                    pygame.mixer.music.stop()

                if result == level.LEVEL_SAVE:
                    save_file = resources.get_save_file()
                    save_state = level.get_state();
                    #save_state["score"] = self.score
                    with shelve.open(str(save_file), "c") as savefile:
                        savefile["game"] = save_state

                if level.terminated():
                    # quit the game on request
                    action = "quit"
                else:
                    # return to the menu
                    action = "menu"
                    highlight_option = 0


if __name__=='__main__':
    Game().run()
