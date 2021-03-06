"""
All fixtures
"""

# some mock classes only have a few methods; that's not a problem
# pylint: disable=too-few-public-methods

# mock class members need to be members even if they don't access self
# pylint: disable=no-self-use

# The way how fixtures work for pytest requires "redefining" outer names
# pylint: disable=redefined-outer-name

import pytest

@pytest.fixture
def fake_color_class():
    """
    Fixture to define a class to mock pygame.Color
    """
    class FakeColor:
        """
        Fake pygame.Color
        """
        def __init__(self, *args):
            self.args = [ "args", args ]


        def set_hsva(self, args):
            """
            Fake hsva; just records the args
            """
            self.args = [ "hsva", args ]


        def get_hsva(self):
            """
            Fake hsva; just returns the args
            """
            if self.args[1] == "hsva":
                return self.args[2]
            return None


        hsva = property(get_hsva, set_hsva)


        def set_hsla(self, args):
            """
            Fake hsla; just records the args
            """
            self.args = [ "hsla", args ]


        def get_hsla(self):
            """
            Fake hsla; just returns the args
            """
            if self.args[1] == "hsla":
                return self.args[2]
            return None


        hsla = property(get_hsla, set_hsla)


    return FakeColor


@pytest.fixture
def dummy_surface():
    """
    Fixture to return a dummy surface class
    """
    class DummySurface:
        """
        Dummy surface
        """
        def __init__(self):
            self.args = None
            self.kwargs = None

        def get_width(self):
            """
            dummy width
            """
            return 42

        def get_height(self):
            """
            dummy height
            """
            return 23

        def blit(self, *args, **kwargs):
            """
            Dummy blit
            """
            self.args = args
            self.kwargs = kwargs

    return DummySurface


@pytest.fixture
def mockclock():
    """
    Return a mock clock
    """
    class MockClock:
        """
        Mock object for pygame.time.Clock
        """
        def __init__(self):
            self.fake_time = 0

        def tick(self, fps):
            """
            Pretent to return elapsed time
            """
            if fps > 0:
                time_leap = (999+fps)//fps
            else:
                time_leap = 1
            self.fake_time += time_leap
            return self.fake_time

    return MockClock


@pytest.fixture
def mockgame(dummy_surface, mockclock):
    """
    Fixture for MockGame
    """
    # pylint: disable=too-few-public-methods
    class MockGame:
        """
        Mock class for game.Game
        """
        def __init__(self):
            self.screen = dummy_surface()
            self.clock = mockclock()
            self.fps = 42

        def toggle_fullscreen(self):
            """
            dummy method
            """

    # pylint: enable=too-few-public-methods
    return MockGame


@pytest.fixture
def mockmedia(dummy_surface):
    """
    Fixture for media.Media
    """
    class MockMedia:
        """
        Mock class for media.Media
        """
        def __init__(self):
            self.screen = dummy_surface()


        def get_screen(self):
            """
            return a dummy surface
            """
            return self.screen

        def tick(self):
            """
            dummy method
            """

        def toggle_fullscreen(self):
            """
            dummy method
            """
    return MockMedia


@pytest.fixture
def dummy_font(dummy_surface):
    """
    Fixture to return dummy  font class
    """
    class DummyFont:
        """
        Dummy font
        """
        def __init__(self, name=None, size=None, bold=False, italic=False):
            self.initargs = [ name, size, bold, italic ]
            self.args = None
            self.kwargs = None
            self.surface = dummy_surface()

        def render(self, *args, **kwargs):
            """
            dummy render
            """
            self.args = args
            self.kwargs = kwargs
            return self.surface

    return DummyFont
