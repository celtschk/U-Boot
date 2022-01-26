import pygame
import resources
from gamedisplay import GameDisplay


class Menu(GameDisplay):
    """
    Class representing a menu.
    """

    def __init__(self, game,
                 menuspec, c_background, c_text, c_highlight, c_message, font,
                 message = None):
        """
        Initialize the menu
        """
        super().__init__(game)
        self.menuspec = menuspec
        self.c_background = c_background
        self.c_text = c_text
        self.c_highlight = c_highlight
        self.c_message = c_message
        self.font = font
        self.selection = 0
        self.message = message


    def draw(self):
        """
        Draw the menu
        """
        screen = self.game.screen
        screen.fill(self.c_background)

        line_height = 50
        center_x = screen.get_width()//2
        center_y = screen.get_height()//2


        current_line = center_y - (len(self.menuspec)-1)*line_height/2

        for index, option in enumerate(self.menuspec):
            if index == self.selection:
                colour = self.c_highlight
            else:
                colour = self.c_text

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
                colour = self.c_message,
                font = self.font,
                origin = (0.5, 0.5)
                )

            text.write(screen)

        pygame.display.flip()


    def handle_event(self, event):
        """
        Handle an event
        """
        if super().handle_event(event):
            return True

        if event.type == pygame.KEYDOWN:
            # If there's a message, any keypress makes it disappear
            self.message = None

            # Up and down navigate the menu
            if event.key == pygame.K_UP:
                if self.selection == 0:
                    self.selection = len(self.menuspec)
                self.selection -= 1
            elif event.key == pygame.K_DOWN:
                self.selection += 1
                if self.selection == len(self.menuspec):
                    self.selection = 0

            # Enter selects an option, thus quits the menu
            elif event.key == pygame.K_RETURN:
                action = self.menuspec[self.selection]["action"]
                if isinstance(action, str):
                    self.quit()
                else:
                    action()


    def get_selected_action(self):
        """
        Get the selected action, or None if a pygame.QUIT event was
        received
        """
        if self.terminated():
            return None
        return self.menuspec[self.selection]["action"]
