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
            self.args = args
            self.hsva_args = None
            self.hsla_args = None
        def hsva(self, *args):
            """
            Fake hsva; just records the args
            """
            self.hsva_args = args
        def hsla(self, *args):
            """
            Fake hsla; just records the args
            """
            self.hsla_args = args

    return FakeColor


# Reusing the name of the fixture as argument is required, not an
# error
# pylint: disable=redefined-outer-name
def test_get_colour_direct_name(mocker, fake_color_class):
    """
    Test getting a colour through get_colour using an actual colour
    name
    """
    mocker.patch("resources.pygame.Color", fake_color_class)
    result = resources.get_colour("red")
    assert isinstance(result, fake_color_class)
    assert result.args == ( "red", )


def test_get_colour_indirect_name(mocker, fake_color_class):
    """
    Test getting a colour through get_colour using an entry leafing to
    an actual colour name
    """
    resources.settings.colours = { "colour": "green" }
    mocker.patch("resources.pygame.Color", fake_color_class)
    result = resources.get_colour("colour")
    assert isinstance(result, fake_color_class)
    assert result.args == ( "green", )


def test_get_colour_double_indirect_name(mocker, fake_color_class):
    """
    Test getting a colour through get_colour using an entry leading to
    another entry which leads to an actual colour name
    """
    resources.settings.colours = { "colour": "pretty", "pretty": "blue" }
    mocker.patch("resources.pygame.Color", fake_color_class)
    result = resources.get_colour("colour")
    assert isinstance(result, fake_color_class)
    assert result.args == ( "blue", )


def test_get_colour_indirect_tuple(mocker, fake_color_class):
    """
    Test getting a colour through get_colour using an entry leading to
    a tuple
    """
    resources.settings.colours = { "colour": (2,3,5,7) }
    mocker.patch("resources.pygame.Color", fake_color_class)
    result = resources.get_colour("colour")
    assert isinstance(result, fake_color_class)
    assert result.args == (2,3,5,7)


def test_get_colour_indirect_dict_rgb(mocker, fake_color_class):
    """
    Test getting a colour through get_colour using an entry leading to
    a tuple
    """
    resources.settings.colours = {
        "colour": { "red": 3, "green": 5, "blue": 7 }
        }
    mocker.patch("resources.pygame.Color", fake_color_class)
    result = resources.get_colour("colour")
    assert isinstance(result, fake_color_class)
    assert result.args == (3,5,7)
