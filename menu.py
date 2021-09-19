import pygame
import resources
from gamedisplay import GameDisplay

class Menu(GameDisplay):
    """
    Class representing a menu.
    """
    def __init__(self, display_info,
                 menuspec, c_background, c_text, c_highlight, font,
                 params = {}):
        super().__init__(display_info)
        self.menuspec = menuspec
        self.c_background = c_background
        self.c_text = c_text
        self.c_highlight = c_highlight
        self.font = font
        self.params = params
        self.selection = 0

    def draw(self):
        self.screen.fill(self.c_background)

        line_height = 50
        center_x = self.screen.get_width()//2
        center_y = self.screen.get_height()//2

        current_line = center_y - (len(self.menuspec)-1)*line_height/2

        for index, option in enumerate(self.menuspec):
            if index == self.selection:
                colour = self.c_highlight
            else:
                colour = self.c_text

            text = resources.MessageData(
                message = option["text"].format(**self.params),
                position = (center_x, current_line),
                colour = colour,
                font = self.font,
                origin = (0.5,0.5) # centered
                )

            text.write(self.screen)

            current_line += line_height

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.terminate()

            if event.type == pygame.KEYDOWN:
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
                    self.quit()

    def get_selected_action(self):
        """
        Get the selected action, or None if a pygame.QUIT event was
        received
        """
        if self.terminated():
            return None
        return self.menuspec[self.selection]["action"]
