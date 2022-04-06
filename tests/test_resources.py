"""
Test resources.py
"""

import pathlib
from functools import partial

import pytest

from src import resources

# some mock classes only have a few methods; that's not a problem
# pylint: disable=too-few-public-methods

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
    mocker.patch('src.resources.pygame.image.load',
                 return_value = Dummy("the image"))
    # make sure the imagestore is initially empty
    mocker.patch.object(resources, "imagestore", {})
    result = resources.load_image("test")
    assert result == "the image"
    assert resources.imagestore["test"] == "the image"


def test_loadimage_existing_image(mocker):
    """
    Test that an existing image is taken straight out of the image store
    """
    # set resources.imagestore to some fake image
    mocker.patch.object(resources, "imagestore", { "foo": "some image" })
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
    assert not result


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
    assert not result


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

@pytest.mark.parametrize(COLOUR_TEST_ARGS, colour_test_data)
def test_get_colour(colours, name, args, mocker, fake_color_class):
    """
    Test getting a colour through get_colour using an entry leafing to
    an actual colour name
    """
    mocker.patch.object(resources.settings, "colours", colours)
    mocker.patch("src.resources.pygame.Color", fake_color_class)
    result = resources.get_colour(name)
    assert isinstance(result, fake_color_class)
    assert result.args == args


def test_get_colour_cycle_detection(mocker):
    """
    Test that a cycle in the colour specification gives an exception
    """
    mocker.patch.object(resources.settings, "colours", { "cyclic": "cyclic" })
    with pytest.raises(ValueError, match = "recursive colour specification"):
        resources.get_colour("cyclic")


def test_get_colour_indirect_cycle_detection(mocker):
    """
    Test that an indirect cycle in the colour specification gives an
    exception
    """
    mocker.patch.object(resources.settings, "colours", {
        "cyclic": "one",
        "one": "two",
        "two": "cyclic" })
    with pytest.raises(ValueError, match = "recursive colour specification"):
        resources.get_colour("cyclic")


def test_sound_store():
    """
    Test that resources.soundstore is initially an emty dictionary
    """
    assert isinstance(resources.sound_store, dict)
    assert not resources.sound_store


def test_getsound_not_loaded(mocker):
    """
    Test that getsound correctly loads a sound and sets its volume
    """
    # pylint: disable=too-few-public-methods
    class FakeSound:
        """
        Mock class for pygame.mixer.Sound
        """
        def __init__(self, filename):
            self.filename = filename
            self.volume = None

        def set_volume(self, volume):
            """
            Store the volume value
            """
            self.volume = volume
    # pylint: enable=too-few-public-methods

    sound_name = "newsound"
    sound_file = "some_file"
    sound_volume = 0.25
    mocker.patch("src.resources.pygame.mixer.Sound", FakeSound)
    mocker.patch.object(resources.settings, "sounds", {
        "newsound": {
            "filename": sound_file,
            "volume": sound_volume
            }
        })
    mocker.patch.object(resources, "sound_store", {})

    result = resources.get_sound(sound_name)

    assert isinstance(result, FakeSound)
    assert result.filename == sound_file
    assert result.volume == sound_volume
    assert sound_name in resources.sound_store
    assert resources.sound_store[sound_name] is result


def test_get_sound_already_loaded(mocker):
    """
    Test that loading a sound already found in sound_store is returned
    directly
    """
    sound_name = "oldsound"
    sound_object = object()

    mocker.patch.object(resources, "sound_store", {
        sound_name: sound_object })

    result = resources.get_sound(sound_name)

    # test that the sound_object is returned
    assert result is sound_object

    # test that the sound store has not changed
    assert resources.sound_store == { sound_name: sound_object }


def test_load_music(mocker):
    """
    Test resources.load_music
    """
    dummy_music_name = "test"
    dummy_filename = "foo"
    dummy_volume = 0.42

    def mock_load(filename):
        assert filename == dummy_filename
    def mock_set_volume(volume):
        assert volume == dummy_volume

    mocker.patch.object(resources.settings, "music", {
        dummy_music_name: { "filename": dummy_filename,
                            "volume": dummy_volume }})

    mocker.patch("src.resources.pygame.mixer.music.load",
                 side_effect = mock_load)

    mocker.patch("src.resources.pygame.mixer.music.set_volume",
                 side_effect = mock_set_volume)

    resources.load_music(dummy_music_name)


def test_get_font(mocker, dummy_font):
    """
    Test resources.get_font
    """
    mocker.patch.object(resources.pygame.font, "SysFont", dummy_font)
    mocker.patch.object(resources.settings, "fonts", {
        "foo": { "name": "aaa", "size": 42 },
        "bar": { "name": "bbb", "size": 23, "bold": True },
        "baz": { "name": "ccc", "size": 69, "italic": True },
        "qux": { "name": "ddd", "size": 13, "bold": True, "italic": True }
        })

    assert resources.get_font("foo").initargs == [ "aaa", 42, False, False ]
    assert resources.get_font("bar").initargs == [ "bbb", 23, True, False ]
    assert resources.get_font("baz").initargs == [ "ccc", 69, False, True ]
    assert resources.get_font("qux").initargs == [ "ddd", 13, True, True ]


def test_message_data(dummy_surface, dummy_font):
    """
    Test the message data class with default arguments and no cached
    data
    """
    font = dummy_font()

    message_template = "test message {foo}, {bar}"

    testobj = resources.MessageData(
        message = message_template,
        position = (3, 5),
        colour = (1, 2, 3),
        font = font
        )

    assert testobj.origin == (0, 0)
    assert testobj.cache == (None, None)

    screen = dummy_surface()

    values = { "foo": "foo value", "bar": "bar value" }
    testobj.write(screen, values)

    expected_text = message_template.format(**values)

    assert testobj.cache == (expected_text, font.surface)

    assert font.args == (expected_text, True, (1, 2, 3))
    assert font.kwargs == {}

    assert screen.args == (font.surface, (3,5))
    assert screen.kwargs == {}


def test_message_data_with_origin(dummy_surface, dummy_font):
    """
    Test the message data class with default arguments and no cached
    data
    """
    font = dummy_font()

    message_template = "test message {foo}, {bar}"

    testobj = resources.MessageData(
        message = message_template,
        position = (3, 5),
        colour = (1, 2, 3),
        font = font,
        origin = (0.5, 0.5)
        )

    assert testobj.cache == (None, None)

    screen = dummy_surface()

    values = { "foo": "foo value", "bar": "bar value" }
    testobj.write(screen, values)

    expected_text = message_template.format(**values)

    assert testobj.cache == (expected_text, font.surface)

    assert font.args == (expected_text, True, (1, 2, 3))
    assert font.kwargs == {}

    assert screen.args == (font.surface,
                           (int(3 - 0.5*font.surface.get_width()),
                            int(5 - 0.5*font.surface.get_height())))
    assert screen.kwargs == {}


def test_message_data_with_function(dummy_surface, dummy_font):
    """
    Test the message data class with default arguments and no cached
    data
    """
    font = dummy_font()

    message_template = "test message {foo}, {bar}"

    def colour(vals):
        return f"colour({vals})"

    testobj = resources.MessageData(
        message = message_template,
        position = (3, 5),
        colour = colour,
        font = font
        )

    assert testobj.origin == (0, 0)
    assert testobj.cache == (None, None)

    screen = dummy_surface()

    values = { "foo": "foo value", "bar": "bar value" }
    testobj.write(screen, values)

    expected_text = message_template.format(**values)

    assert testobj.cache == (expected_text, font.surface)

    assert font.args == (expected_text, True, f"colour({values})")
    assert font.kwargs == {}

    assert screen.args == (font.surface, (3,5))
    assert screen.kwargs == {}


def test_message_data_cached(dummy_surface, dummy_font):
    """
    Test that the write method correctly uses cached data
    """
    font = dummy_font()
    message_template = "test message {foo}, {bar}"
    values = { "foo": "foo value", "bar": "bar value" }
    expected_text = message_template.format(**values)
    screen = dummy_surface()

    # pylint: disable=unused-argument
    def never_call(data):
        assert False, "This line should never be executed"
    # pylint: enable=unused-argument

    testobj = resources.MessageData(
        message = message_template,
        position = (3, 5),
        colour = never_call,
        font = font
        )

    # manually set up the cache
    testobj.cache = (expected_text, font.surface)

    testobj.write(screen, values)

    # the cache should not have changed
    assert testobj.cache == (expected_text, font.surface)

    assert font.args is None
    assert font.args is None

    assert screen.args == (font.surface, (3,5))
    assert screen.kwargs == {}

def test_message_data_changed(dummy_surface, dummy_font):
    """
    Test that the write method ignores cached data if values have
    changed
    """
    font = dummy_font()
    message_template = "test message {foo}, {bar}"

    old_values = { "foo": "foo value", "bar": "bar value" }
    old_expected_text = message_template.format(**old_values)

    values = { "foo": "other foo value", "bar": "other bar value" }
    expected_text = message_template.format(**values)

    screen = dummy_surface()

    testobj = resources.MessageData(
        message = message_template,
        position = (3, 5),
        colour = "red",
        font = font
        )

    # manually set up the cache
    testobj.cache = (old_expected_text, None)

    testobj.write(screen, values)

    # the cache should have changed
    assert testobj.cache == (expected_text, font.surface)

    assert font.args == (expected_text, True, "red")
    assert font.kwargs == {}

    assert screen.args == (font.surface, (3,5))
    assert screen.kwargs == {}


def test_get_value(mocker):
    """
    Test resources.get_value
    """
    mocker.patch.object(resources.random, "uniform",
                        lambda x, y: (x, y))

    assert resources.get_value(42) == 42
    assert resources.get_value({"min": 10, "max": 20}) == (10, 20)


def test_randomly_true(mocker):
    """
    Test resources.randomly_true
    """
    x_value = None
    y_value = None
    def uniform(arg_x, arg_y):
        nonlocal x_value
        nonlocal y_value
        x_value = arg_x
        y_value = arg_y
        return 0.5

    mocker.patch.object(resources.random, "uniform", uniform)

    assert not resources.randomly_true(0.3)
    assert x_value == 0
    assert y_value == 1
    assert resources.randomly_true(0.7)


def test_get_save_file(mocker, tmp_path):
    """
    test get_save_file
    """
    def mock_user_data_dir(appname, appauthor, version):
        return tmp_path / appname / appauthor / version
    mocker.patch.object(resources.appdirs, "user_data_dir",
                        mock_user_data_dir)
    mocker.patch.object(resources.settings, "game_info", {
        "name": "Name",
        "author": "Author",
        "version": "Version"
        })
    mocker.patch.object(resources.settings, "save_file", "File")

    result = resources.get_save_file()
    assert isinstance(result, pathlib.Path)
    assert result.as_posix() == tmp_path.as_posix() + "/Name/Author/Version/File"


def test_try_load_all(mocker):
    """
    test try_load_all function
    """
    all_names = { "foo", "bar", "baz0", "baz1", "baz2",
                  "qux1", "qux2", "quux", "red", "green", "blue" }
    seen_names = set()

    mocker.patch.object(resources.settings, "objects", {
        "foo_object": {
            "initdata": {
                "filename": "foo"
                }
            },
        "bar_object": {
            "initdata": {
                "filename": "bar"
                }
            }
        })

    mocker.patch.object(resources.settings, "animations", {
        "baz_animation": {
            "frame_count": 3,
            "images": "baz{frame}"
            }
        })

    mocker.patch.object(resources.settings, "sounds", {
        "sound1": "qux1",
        "sound2": "qux2"
        })

    mocker.patch.object(resources.settings, "music", {
        "music": "quux"
        })

    mocker.patch.object(resources.settings, "colours", {
        "colour1": "red",
        "colour2": "green",
        "colour3": "blue"
        })

    def mock_load_image(filename):
        nonlocal seen_names
        seen_names.add(filename)

    def mock_get(mapping, key):
        nonlocal seen_names
        seen_names.add(mapping[key])

    mocker.patch.object(resources, "load_image", mock_load_image)
    mocker.patch.object(resources, "get_sound",
                        partial(mock_get, resources.settings.sounds))
    mocker.patch.object(resources, "load_music",
                        partial(mock_get, resources.settings.music))
    mocker.patch.object(resources, "get_colour",
                        partial(mock_get, resources.settings.colours))

    resources.try_load_all()

    assert seen_names == all_names

DICTIONARY_TEST_ARGS = "old, update, new"

dictionary_test_data = [
    # Updating an empty directory with an empty directory does nothing
    ( { }, { }, { } ),

    # Updating a non-empty directory with an emty directory does nothing
    ( { "foo": 1 }, { }, { "foo": 1 } ),

    # Replacement of one value
    ( { "foo": 1, "bar": 2 }, { "foo": 3 }, { "foo": 3, "bar": 2 } ),

    # Addition of a new value
    ( { "foo": 1 }, { "bar": 2 }, { "foo":1, "bar": 2 } ),

    # Removal of a value
    ( { "foo": 1, "bar": 2 }, { "foo": None }, { "bar": 2 } ),

    # Adding a value to a nested dict
    ( { "foo": { "bar": 3 } }, { "foo": { "baz": 5 } },
      { "foo": { "bar": 3, "baz": 5 } } ),

    # Updating in several levels at once
    ( { "foo": { "bar": { "baz": 1 } } },
      { "foo2": 2, "foo": { "bar2": 3, "bar": { "baz": 5 } } },
      { "foo": { "bar": { "baz": 5 }, "bar2": 3 }, "foo2": 2 } ),

    # Deleting a key whose value is a dict
    ( { "foo": { "bar": 3 } }, { "foo": None }, { } ),
    ]

@pytest.mark.parametrize(DICTIONARY_TEST_ARGS, dictionary_test_data)
def test_recursive_update(old, update, new):
    """
    Test the recursive update function
    """
    resources.recursive_update(old, update)
    assert old == new


def test_bisect():
    """
    Test the bisect function
    """
    assert resources.bisect(3, 16, lambda x: x < 10) == 10
    assert resources.bisect(3, 16, lambda x: x < 20) == 16
    assert resources.bisect(3, 16, lambda x: True) == 16
    assert resources.bisect(3, 3, lambda x: True) == 3
