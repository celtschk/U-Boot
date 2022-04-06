"""
Test the GameDisplay class
"""

import pytest

import pygame

from src.gamedisplay import GameDisplay

@pytest.fixture
def mockgame():
    class MockGame:
        def toggle_fullscreen(self):
            pass
    return MockGame

def test_class():
    """
    Test subclass and class members
    """
    assert 'Status' in GameDisplay.__dict__
    assert 'INITIALIZED' in GameDisplay.__dict__
    assert isinstance(GameDisplay.INITIALIZED, GameDisplay.Status)
    assert 'RUNNING' in GameDisplay.__dict__
    assert isinstance(GameDisplay.RUNNING, GameDisplay.Status)
    assert 'TERMINATE' in GameDisplay.__dict__
    assert isinstance(GameDisplay.TERMINATE, GameDisplay.Status)
    assert 'QUIT' in GameDisplay.__dict__
    assert isinstance(GameDisplay.QUIT, GameDisplay.Status)


def test_GameDisplay_init(mockgame):
    """
    Test the members of a newly created GameDisplay onject
    """
    mock_game = mockgame()
    game_display = GameDisplay(mock_game)
    assert hasattr(game_display, 'game')
    assert game_display.game is mock_game

    assert hasattr(game_display, 'status')
    assert game_display.status == GameDisplay.INITIALIZED

    assert hasattr(game_display, 'running_statuses')
    assert isinstance(game_display.running_statuses, set)
    assert game_display.running_statuses == { GameDisplay.RUNNING }

    assert hasattr(game_display, 'key_bindings')
    assert isinstance(game_display.key_bindings, dict)
    assert pygame.K_f in game_display.key_bindings
    assert game_display.key_bindings[pygame.K_f] == mock_game.toggle_fullscreen
    assert pygame.K_HASH in game_display.key_bindings
    assert (game_display.key_bindings[pygame.K_HASH] ==
            game_display._GameDisplay__screenshot)


def test_GameDisplay_is_running(mockgame):
    """
    Test the is_running member
    """
    game_display = GameDisplay(mockgame())

    assert not game_display.is_running()

    game_display.status = GameDisplay.RUNNING
    assert game_display.is_running()

    game_display.status = GameDisplay.TERMINATE
    assert not game_display.is_running()

    game_display.status = GameDisplay.QUIT
    assert not game_display.is_running()

