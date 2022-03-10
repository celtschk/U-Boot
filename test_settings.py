"""
Test the validity of entries in settings
"""

import re
import pygame
import settings


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


def test_font():
    """
    Test that font specification is valid
    """
    assert isinstance(settings.font, dict)
    assert "name" in settings.font
    assert "size" in settings.font
    assert isinstance(settings.font["name"], str)
    assert isinstance(settings.font["size"], int)
    assert settings.font["size"] > 0


def test_paginated_font():
    """
    Test that paginated_font specification is valid
    """
    assert isinstance(settings.paginated_font, dict)
    assert "name" in settings.paginated_font
    assert "size" in settings.paginated_font
    assert isinstance(settings.paginated_font["name"], str)
    assert isinstance(settings.paginated_font["size"], int)
    assert settings.paginated_font["size"] > 0
