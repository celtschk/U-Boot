"""
Test resources.py
"""

import pytest

import resources

def test_imagestore():
    """
    Test that theimagestore variable exists, is a dictionary, and
    starts out empty
    """
    assert isinstance(resources.imagestore, dict)
    assert not resources.imagestore


def test_loadimage_new_image(mocker):
    """
    Test that a new image is properly loaded and stored in the
    imagestore
    """
    # pylint: disable=too-few-public-methods
    class Dummy:
        """
        A dummy class to stand for the result of pygame.image.load
        """
        def __init__(self, string):
            self.string = string
        def convert_alpha(self):
            """
            This mocks pygame.Surface.convert_alpha
            """
            return self.string
    # pylint: enable=too-few-public-methods
    mocker.patch('resources.pygame.image.load',
                 return_value = Dummy("the image"))
    # make sure the imagestore is initially empty
    resources.imagestore = {}
    result = resources.load_image("test")
    assert result == "the image"
    assert resources.imagestore["test"] == "the image"


def test_loadimage_existing_image():
    """
    Test that an existing image is taken straight out of the image store
    """
    # set resources.imagestore to some fake image
    resources.imagestore = { "foo": "some image" }
    result = resources.load_image("foo")
    assert result == "some image"


def test_subset_or_none_with_subset():
    """
    Test resources.subset_or_none when the second directory is a
    subset
    """
    dict1 = { 1: 10, 2: 20, 3: 30 }
    dict2 = { 1: 11, 3: 31 }
    result = resources.subset_or_none(dict1, dict2)
    assert isinstance(result, dict)
    assert result ==  { 1: 11, 2: 20, 3: 31 }


def test_subset_or_none_with_not_subset():
    """
    Test resources.subset_or_none when the second directory is a
    subset
    """
    dict1 = { 1: 10, 2: 20, 3: 30 }
    dict2 = { 1: 11, 4: 31 }
    result = resources.subset_or_none(dict1, dict2)
    assert isinstance(result, dict)
    assert result ==  {}


class MyDict(dict):
    """
    Dictionary, but with user defined type
    """


class MyDict2(dict):
    """
    Dictionary, but with other user defined type
    """


def test_subset_or_none_with_mydict_and_subset():
    """
    Test resources.subset_or_none when the second directory is a
    subset
    """
    dict1 = MyDict({ 1: 10, 2: 20, 3: 30 })
    dict2 = MyDict2({ 1: 11, 3: 31 })
    result = resources.subset_or_none(dict1, dict2)
    assert isinstance(result, MyDict)
    assert result ==  { 1: 11, 2: 20, 3: 31 }


def test_subset_or_none_with_mydict_and_not_subset():
    """
    Test resources.subset_or_none when the second directory is a
    subset
    """
    dict1 = MyDict({ 1: 10, 2: 20, 3: 30 })
    dict2 = MyDict2({ 1: 11, 4: 31 })
    result = resources.subset_or_none(dict1, dict2)
    assert isinstance(result, MyDict)
    assert result ==  {}


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


COLOUR_TEST_ARGS = "colours, name, args"

colour_test_data = [
    # function is given an actual colour name (i.e. a name that's not
    # in settings.colours), should pass it on
    ( {}, "colourname", [ "args", ( "colourname", ) ] ),

    # function is given an entry in settings.colours that leads
    # directly to an actual colour name, should give the value
    # from entry.
    ( { "direct": "green" }, "direct", [ "args", ( "green", ) ] ),

    # an entry that leads to another entry should be resolved
    # recursively
    ( { "indirect": "pretty", "pretty": "blue" }, "indirect",
      [ "args", ( "blue", ) ] ),

    # an entry that leads to a tuple should pass that tuple to
    # pygame.Color
    ( { "tuple": (2,3,5,7) }, "tuple", [ "args", (2,3,5,7) ] ),

    # an entry using a dictionary with entries "red", "green", "blue"
    # should pass them directly as constructor arguments
    ( { "rgb": { "red": 3, "green": 5, "blue": 7 } }, "rgb",
      [ "args", (3,5,7) ] ),

    # if any of them are omitted, its value should be assumed to be 0
    ( { "rg": { "red": 3, "green": 5 } }, "rg", [ "args", (3,5,0) ] ),
    ( { "rb": { "red": 3, "blue": 7 } }, "rb", [ "args", (3,0,7) ] ),
    ( { "gb": { "green": 5, "blue": 7 } }, "gb", [ "args", (0,5,7) ] ),
    ( { "only red": { "red": 3 } }, "only red", [ "args", (3,0,0) ] ),
    ( { "only green": { "green": 5 } }, "only green", [ "args", (0,5,0) ] ),
    ( { "only blue": { "blue": 7 } }, "only blue", [ "args", (0,0,7) ] ),
    ( { "empty": {} }, "empty", [ "args", (0,0,0) ] ),

    # a "gray" or "grey" value should be passed to all three channels
    ( { "gray value": { "gray": 42 } }, "gray value", [ "args", (42,42,42) ] ),
    ( { "grey value": { "grey": 42 } }, "grey value", [ "args", (42,42,42) ] ),

    # a dictionary with "hue", "saturation", "value" should use the
    # hsva property
    ( { "hsv": { "hue": 30, "saturation": 60, "value": 95 } }, "hsv",
        [ "hsva", (30, 60, 95, 100) ] ),

    # omitting some but not all results in using the corresponging
    # default values
    ( { "hs": { "hue": 30, "saturation": 60 } }, "hs",
        [ "hsva", (30, 60, 100, 100) ] ),
    ( { "hv": { "hue": 30, "value": 95 } }, "hv",
        [ "hsva", (30, 100, 95, 100) ] ),
    ( { "sv": { "saturation": 60, "value": 95 } }, "sv",
        [ "hsva", (0, 60, 95, 100) ] ),
    ( { "only hue": { "hue": 30 } }, "only hue",
        [ "hsva", (30, 100, 100, 100) ] ),
    ( { "only saturation": { "saturation": 60 } }, "only saturation",
        [ "hsva", (0, 60, 100, 100) ] ),
    ( { "only value": { "hue": 30, "value": 95 } }, "only value",
        [ "hsva", (30, 100, 95, 100) ] ),

    # a dictionary with "hue", "saturation", "lightness" should use the
    # hsla property
    ( { "hsl": { "hue": 30, "saturation": 60, "lightness": 95 } }, "hsl",
        [ "hsla", (30, 60, 95, 100) ] ),

    # omitting some of then gives default values, but "lightness"
    # cannot be omitted, as that would lead to hsv being useed
    ( { "hl": { "hue": 30, "lightness": 95 } }, "hl",
        [ "hsla", (30, 100, 95, 100) ] ),
    ( { "sl": { "saturation": 60, "lightness": 95 } }, "sl",
        [ "hsla", (0, 60, 95, 100) ] ),
    ( { "only lightness": { "lightness": 95 } }, "only lightness",
        [ "hsla", (0, 100, 95, 100) ] ),
]

# Reusing the name of the fixture as argument is required, not an
# error, thus shut up pylint about this
# pylint: disable=redefined-outer-name

@pytest.mark.parametrize(COLOUR_TEST_ARGS, colour_test_data)
def test_get_colour(colours, name, args, mocker, fake_color_class):
    """
    Test getting a colour through get_colour using an entry leafing to
    an actual colour name
    """
    mocker.patch.object(resources.settings, "colours", colours)
    mocker.patch("resources.pygame.Color", fake_color_class)
    result = resources.get_colour(name)
    assert isinstance(result, fake_color_class)
    assert result.args == args
