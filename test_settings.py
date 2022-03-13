"""
Test the validity of entries in settings
"""

import re
from os.path import isfile
from numbers import Number
from copy import deepcopy

import pygame

import settings
import resources


def test_game_name_is_string():
    """
    Test that the game name is of type str
    """
    assert isinstance(settings.game_name, str)


def test_game_title_is_string():
    """
    Test that the game name is of type str
    """
    assert isinstance(settings.game_title, str)


def test_game_version_is_string():
    """
    Test that game_version is a string
    """
    assert isinstance(settings.game_version, str)


def test_game_version_is_valid_version_number():
    """
    Test that game_version contains a valid version nnumber.

    A valid version number is a sequence of two or more non-negative
    integers separated by dots, with no spaces.
    """
    version_number_regex = re.compile(r"^[0-9]+(\.[0-9]+)*$")
    assert version_number_regex.match(settings.game_version) is not None


def test_game_author_is_string():
    """
    Test that game_author is a string
    """
    assert isinstance(settings.game_author, str)


def test_width_is_positive_integer():
    """
    Test that width is a positive integer
    """
    assert isinstance(settings.width, int)
    assert settings.width > 0


def test_height_is_positive_integer():
    """
    Test that height is a positive integer
    """
    assert isinstance(settings.height, int)
    assert settings.height > 0


def test_sky_fraction_is_fraction():
    """
    Test that sky_fraction is a number between 0.0 and 1.0
    """
    assert 0.0 <= settings.sky_fraction <= 1.0


def test_fps_is_positive_integer():
    """
    Test that fps is a positive integer
    """
    assert isinstance(settings.fps, int)
    assert settings.fps > 0


def test_score_frames_is_positive_integer():
    """
    Test that score_frames is a positive integer
    """
    assert isinstance(settings.score_frames, int)
    assert settings.score_frames > 0


def test_level_display_frames_is_positive_integer():
    """
    Test that level_display_frames is a positive integer
    """
    assert isinstance(settings.level_display_frames, int)
    assert settings.level_display_frames > 0


def test_colours_is_dict():
    """
    Test that colours is a dict
    """
    assert isinstance(settings.colours, dict)


def test_colour_names_are_strings():
    """
    Test that the colour names are all strings
    """
    for colour in settings.colours:
        assert isinstance(colour, str)


def test_colour_values():
    """
    Test that colour values ultimately lead to valid arguments to
    pygame.Color
    """
    for value in settings.colours.values():
        # detect infinite loops
        seen_values = { value }

        while value in settings.colours:
            value = settings.colours[value]
            assert value not in seen_values
            seen_values.add(value)

        # If value is not a valid colour specification, this gives a
        # ValueError exception
        pygame.Color(value)


def verify_dict_entry(dictionary, name, entry_type,
                      condition = lambda value: True):
    """
    Verify that a dict entry of a given name exists and its value has
    the required type and properties
    """
    assert name in dictionary
    assert isinstance(dictionary[name], entry_type)
    assert condition(dictionary[name])


def is_positive(number):
    """
    Gives True if the number is positive, False otherwise
    """
    return number > 0


def is_nonnegative(number):
    """
    Gives True if the number is non-negative, False otherwise
    """
    return number >= 0


def is_fraction(number):
    """
    Gives True if the number is a fraction (i.e. between 0 and 1)
    """
    return 0.0 <= number <= 1.0


def test_font():
    """
    Test that font specification is valid
    """
    assert isinstance(settings.font, dict)
    verify_dict_entry(settings.font, "name", str)
    verify_dict_entry(settings.font, "size", int, is_positive)


def test_paginated_font():
    """
    Test that paginated_font specification is valid
    """
    assert isinstance(settings.paginated_font, dict)
    verify_dict_entry(settings.paginated_font, "name", str)
    verify_dict_entry(settings.paginated_font, "size", int, is_positive)


def test_paginate_layout():
    """
    Test that the paginated_layout specification is valid
    """
    assert isinstance(settings.paginate_layout, dict)

    verify_dict_entry(settings.paginate_layout, "border", dict)
    verify_dict_entry(settings.paginate_layout, "line spacing", int,
                      is_positive)

    verify_dict_entry(settings.paginate_layout["border"], "top", int,
                      is_nonnegative)
    verify_dict_entry(settings.paginate_layout["border"], "left", int,
                      is_nonnegative)
    verify_dict_entry(settings.paginate_layout["border"], "right", int,
                      is_nonnegative)
    verify_dict_entry(settings.paginate_layout["border"], "bottom", int,
                      is_nonnegative)


def verify_sound_spec(sound_spec):
    """
    Check for valid sound specification
    """
    assert isinstance(sound_spec, dict)
    verify_dict_entry(sound_spec, "filename", str, isfile)
    verify_dict_entry(sound_spec, "volume", Number, is_fraction)


def test_sounds():
    """
    Test sounds dictionary
    """
    assert isinstance(settings.sounds, dict)
    for sound, properties in settings.sounds.items():
        assert isinstance(sound, str)
        verify_sound_spec(properties)


def test_animations():
    """
    Test animations dictionary
    """
    assert isinstance(settings.animations, dict)
    for animation, properties in settings.animations.items():
        assert isinstance(animation, str)
        assert isinstance(properties, dict)
        verify_dict_entry(properties, "fps", int, is_positive)
        verify_dict_entry(properties, "frame_count", int, is_positive)
        verify_dict_entry(properties, "images", str)
        for frame in range(properties["frame_count"]):
            assert isfile(properties["images"].format(frame = frame))


def test_music():
    """
    Test music dictionary
    """
    assert isinstance(settings.music, dict)
    for name, properties in settings.music.items():
        assert isinstance(name, str)
        assert isinstance(properties, dict)
        verify_dict_entry(properties, "filename", str, isfile)
        verify_dict_entry(properties, "volume", Number, is_fraction)


def is_num_or_range(item):
    """
    Returns true if the item is either a numberof a valid range
    specification
    """
    if isinstance(item, Number):
        return True
    if not isinstance(item, dict):
        return False
    if item.keys() != { "min", "max" }:
        return False
    if not isinstance(item["min"], Number):
        return False
    if not isinstance(item["max"], Number):
        return False
    return item["min"] < item["max"]


def verify_movement(movement, constant_names):
    """
    Verify correctness of object movement specification
    """
    verify_dict_entry(movement, "start", tuple,
                      lambda pair: len(pair) == 2)

    first_string_options = { "left", "right", "ship" }
    first_string_options.update(constant_names)

    second_string_options = { "ship" }
    second_string_options.update(constant_names)

    if isinstance(movement["start"][0], str):
        assert movement["start"][0] in first_string_options
    else:
        assert isinstance(movement["start"][0], Number)

    if isinstance(movement["start"][1], str):
        assert movement["start"][1] in second_string_options
    else:
        assert isinstance(movement["start"][1], Number)

    verify_dict_entry(movement, "speed", object, is_num_or_range)
    verify_dict_entry(movement, "direction", tuple,
                      lambda pair: len(pair) == 2)

    assert isinstance(movement["direction"][0], Number)
    assert isinstance(movement["direction"][1], Number)

    verify_dict_entry(movement, "repeat", bool)


def test_objects():
    """
    Test objects dictionary
    """
    # the actual tests are moved to a separate function so that they
    # can be reused for testing level_updates
    verify_objects(settings.objects)


def verify_objects(object_dict):
    """
    Verify
    """
    assert isinstance(object_dict, dict)
    for name, properties in object_dict.items():
        assert isinstance(name, str)
        assert isinstance(properties, dict)
        verify_dict_entry(properties, "filename", str, isfile)
        verify_dict_entry(properties, "origin", tuple,
                          lambda pair: len(pair) == 2)
        assert isinstance(properties["origin"][0], Number)
        assert isinstance(properties["origin"][1], Number)
        verify_dict_entry(properties, "movement", dict)

        if "constants" in properties:
            constants = properties["constants"]
            assert isinstance(constants, dict)
            for key, value in constants.items():
                assert isinstance(key, str)
                assert is_num_or_range(value)
        else:
            constants = {}

        verify_movement(properties["movement"], constants.keys())

        if "max_count" in properties:
            assert "total_count" in properties
        if "total_count" in properties:
            assert "max_count" in properties
            verify_dict_entry(properties, "max_count", int, is_positive)
            verify_dict_entry(properties, "total_count", int, is_positive)

        if "to_destroy" in properties:
            verify_dict_entry(properties, "to_destroy", int, is_positive)

        if "spawn_rate" in properties:
            verify_dict_entry(properties, "spawn_rate", Number, is_positive)


def test_hit_info():
    """
    Test the hit_info directory
    """
    assert isinstance(settings.hit_info, dict)
    for key, value in settings.hit_info.items():
        assert isinstance(key, tuple)
        assert len(key) == 2

        assert isinstance(key[0], str)
        assert key[0] in settings.objects

        assert isinstance(key[1], str)
        assert key[1] in settings.objects

        assert isinstance(value, dict)

        assert "animation" in value
        assert isinstance(value["animation"], str)
        assert value["animation"] in settings.animations

        assert "sound" in value
        assert isinstance(value["sound"], str)
        assert value["sound"] in settings.sounds

        assert "score" in value
        assert isinstance(value["score"], bool)


# this test is incomplete
def test_level_updates():
    """
    Test settings.level_updates
    """
    assert isinstance(settings.level_updates, dict)
    for level, updates in settings.level_updates.items():
        assert isinstance(level, int)
        assert is_positive(level)
        assert isinstance(updates, dict)

        level_objects = deepcopy(settings.objects)
        resources.recursive_update(level_objects, updates)
        verify_objects(level_objects)


def test_save_file():
    """
    Test that save_file is a non_empty string
    """
    assert isinstance(settings.save_file, str)
    assert settings.save_file != ""


def test_screenshot_file():
    """
    Test that screenshot_file is a non_empty string
    """
    assert isinstance(settings.save_file, str)
    assert settings.save_file != ""
