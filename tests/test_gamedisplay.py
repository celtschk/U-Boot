"""
Test the GameDisplay class
"""
# pylint: disable=invalid-name
# pylint: disable=protected-access

import pytest

import pygame

from src.gamedisplay import GameDisplay

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
    # Comparison with callable is indeed intended
    # pylint: disable=comparison-with-callable
    assert game_display.key_bindings[pygame.K_f] == mock_game.toggle_fullscreen
    assert pygame.K_HASH in game_display.key_bindings
    assert (game_display.key_bindings[pygame.K_HASH] ==
            game_display._GameDisplay__screenshot)
    # pylint: enable=comparison-with-callable


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


def test_GameDisplay_draw(mockgame):
    """
    Test GameDisplay.draw
    """
    with pytest.raises(NotImplementedError):
        GameDisplay(mockgame()).draw()


event_cases = [
    (pygame.event.Event(pygame.KEYDOWN, key=pygame.K_x),
     False, False, False, GameDisplay.RUNNING),
    (pygame.event.Event(pygame.KEYDOWN, key=pygame.K_f),
     True, True, False, GameDisplay.RUNNING),
    (pygame.event.Event(pygame.KEYDOWN, key=pygame.K_b),
     True, False, True, GameDisplay.RUNNING),
    (pygame.event.Event(pygame.QUIT),
     True, False, False, GameDisplay.TERMINATE)
    ]

# pylint: disable=too-many-arguments
@pytest.mark.parametrize("event, handled, call_foo, call_bar, status", event_cases)
def test_GameDisplay_handle_event(event, handled, call_foo, call_bar, status,
                                  mockgame):
    """
    Test GameDisplay.handle_event
    """
    function_foo_called = function_bar_called = False
    def function_foo():
        nonlocal function_foo_called
        function_foo_called = True
    def function_bar():
        nonlocal function_bar_called
        function_bar_called = True

    game_display = GameDisplay(mockgame())
    game_display.key_bindings = {
        pygame.K_f: function_foo,
        pygame.K_b: function_bar
        }
    game_display.status = GameDisplay.RUNNING

    event_handled = game_display.handle_event(event)
    assert isinstance(event_handled, bool)
    assert event_handled == handled
    assert function_foo_called == call_foo
    assert function_bar_called == call_bar
    assert game_display.status == status
