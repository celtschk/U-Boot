"""
This module provides the GameDisplay class
"""

import pygame

class GameDisplay:
    """
    Base class containing the logic of any screen the user may
    interact with, whether it is the gameplay or a menu.
    """
    # exit status values (not an enum, because derived classes
    # will want to add more. Also, no need for numeric values;
    # equality comparison is fully sufficient
    class Status:
        """
        Empty class to define unique status values
        """

    TERMINATE = Status()
    QUIT = Status()


    def __init__(self, game):
        """
        Initializes the GameDisplay object
        """
        self.game = game
        self.running = False
        self.status = None


    def draw(self):
        """
        Draws the object.

        To be supplied by the derived class.
        """
        raise NotImplementedError("Must be supplied by the derived class")


    def handle_event(self, event):
        """
        Handle a known event. Returns if the event has been handled.

        This function handles pygame.QUIT and toggling fullscreen with
        key F. To handle other events, override this function.
        """
        # A pygame.QUIT event always terminates the game completely
        if event.type == pygame.QUIT:
            self.terminate()
            return True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                self.game.toggle_fullscreen()
                return True
            if event.key == pygame.K_HASH:
                pygame.image.save(self.game.screen, "U-Boot-screenshot.png")
                return True

        # If we get here, no event has been handled.
        return False


    def update_state(self):
        """
        Updates the state.

        Does nothing in the base class. Can, but does not need to be
        overwritten by the derived class.
        """


    def ready_to_quit(self):
        """
        Returns True if the level can actually be quit.

        This method always returns True. It can be overridden by a
        derived class to allow delayed quitting, e.g. to display a
        message.

        When quit() has been called, but this function returns False,
        the event loop still continues, but self.running is false.

        This function is only called from the event loop if
        self.running == False.
        """
        return True


    def execute(self):
        """
        The main loop
        """
        self.running = True
        while self.running or not self.ready_to_quit():
            self.draw()
            self.game.clock.tick(self.game.fps)
            for event in pygame.event.get():
                self.handle_event(event)
            self.update_state()
        return self.status


    def quit(self, status = QUIT):
        """
        Quit the display, but not necessarily the game
        """
        assert isinstance(status, self.Status)
        self.running = False
        self.status = status


    def terminate(self):
        """
        Quit the game
        """
        self.quit(self.TERMINATE)


    def terminated(self):
        """
        Returns whether the terminate function was called.
        """
        return self.status == self.TERMINATE
