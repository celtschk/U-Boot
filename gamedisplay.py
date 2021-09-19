import pygame

class GameDisplay:
    """
    Base class containing the logic of any screen the user may
    interact with, whether it is the gameplay or a menu.
    """
    def __init__(self, screen, clock, fps):
        """
        Initializes the GameDisplay object
        """
        self.screen = screen
        self.clock = clock
        self.fps = fps
        self.running = False
        self.quit_game = False

    def draw(self):
        """
        Draws the object.

        To be supplied by the derived class.
        """
        raise NotImplementedError("Must be supplied by the derived class")

    def handle_events(self):
        """
        Handles the events.

        To be supplied by the derived clas.
        """
        raise NotImplementedError("Must be supplied by the derived class")

    def update_state(self):
        """
        Updates the state.

        Does nothing in the base class. Can, but does not need to be
        overwritten by the derived class.
        """
        pass

    def execute(self):
        """
        The main loop
        """
        self.running = True
        while self.running:
            self.draw()
            self.clock.tick(self.fps)
            self.handle_events()
            self.update_state()

    def quit(self):
        """
        Quit the display, but not necessarily the game
        """
        self.running = False

    def terminate(self):
        """
        Quit the game
        """
        self.quit()
        self.quit_game = True

    def terminated(self):
        """
        Returns whether the terminate function was called.
        """
        return self.quit_game
