import pygame

class GameDisplay:
    """
    Base class containing the logic of any screen the user may
    interact with, whether it is the gameplay or a menu.
    """
    def __init__(self, game):
        """
        Initializes the GameDisplay object
        """
        self.game = game
        self.running = False
        self.quit_game = False


    def draw(self):
        """
        Draws the object.

        To be supplied by the derived class.
        """
        raise NotImplementedError("Must be supplied by the derived class")


    def handle_event(self, event):
        """
        Handle a known event. Returns if the event has been handled.

        This function handles only pygame.QUIT. To handle other events,
        override this function.
        """
        # A pygame.QUIT event always terminates the game completely
        if event.type == pygame.QUIT:
            self.terminate()
            return True

        # If we get here, no event has been handled.
        return False


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
            self.game.clock.tick(self.game.fps)
            for event in pygame.event.get():
                self.handle_event(event)
            self.update_state()
        return self.status


    def quit(self, status = None):
        """
        Quit the display, but not necessarily the game
        """
        self.running = False
        self.status = status


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
