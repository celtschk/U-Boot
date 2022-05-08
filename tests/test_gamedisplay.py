"""
Test the GameDisplay class
"""
# pylint: disable=invalid-name
# pylint: disable=protected-access

import pytest

import pygame

from src import gamedisplay
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

    assert 'EVENT_HIDE_MOUSE' in GameDisplay.__dict__
    assert isinstance(GameDisplay.EVENT_HIDE_MOUSE, int)
    assert GameDisplay.EVENT_HIDE_MOUSE == 1


def test_GameDisplay_init(mockmedia, dummy_font):
    """
    Test the members of a newly created GameDisplay onject
    """
    mock_media = mockmedia()
    font = dummy_font()
    game_display = GameDisplay(mock_media, font)
    assert hasattr(game_display, 'media')
    assert game_display.media is mock_media

    assert hasattr(game_display, 'font')
    assert game_display.font is font

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
    assert game_display.key_bindings[pygame.K_f] == mock_media.toggle_fullscreen
    assert pygame.K_HASH in game_display.key_bindings
    assert (game_display.key_bindings[pygame.K_HASH] ==
            game_display._GameDisplay__screenshot)
    # pylint: enable=comparison-with-callable


def test_GameDisplay_is_running(mockmedia, dummy_font):
    """
    Test the is_running member
    """
    game_display = GameDisplay(mockmedia(), dummy_font())

    assert not game_display.is_running()

    game_display.status = GameDisplay.RUNNING
    assert game_display.is_running()

    game_display.status = GameDisplay.TERMINATE
    assert not game_display.is_running()

    game_display.status = GameDisplay.QUIT
    assert not game_display.is_running()


def test_GameDisplay_draw(mockmedia, dummy_font):
    """
    Test GameDisplay.draw
    """
    with pytest.raises(NotImplementedError):
        GameDisplay(mockmedia(), dummy_font()).draw()


event_cases = [
    (pygame.event.Event(pygame.KEYDOWN, key=pygame.K_x),
     False, False, False, None, False, GameDisplay.RUNNING),
    (pygame.event.Event(pygame.KEYDOWN, key=pygame.K_f),
     True, True, False, None, False, GameDisplay.RUNNING),
    (pygame.event.Event(pygame.KEYDOWN, key=pygame.K_b),
     True, False, True, None, False, GameDisplay.RUNNING),
    (pygame.event.Event(pygame.QUIT),
     True, False, False, None, False, GameDisplay.TERMINATE),
    (pygame.event.Event(pygame.USEREVENT, event=GameDisplay.EVENT_HIDE_MOUSE),
     True, False, False, False, False, GameDisplay.RUNNING),
    (pygame.event.Event(pygame.MOUSEMOTION),
     True, False, False, None, True, GameDisplay.RUNNING),
    ]

# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
@pytest.mark.parametrize(
    "event, handled, call_foo, call_bar, call_is_visible, call_show, status",
    event_cases)
def test_GameDisplay_handle_event(event, handled,
                                  call_foo, call_bar,
                                  call_is_visible, call_show,
                                  status,
                                  mocker, mockmedia, dummy_font):
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

    def set_visible(is_visible):
        set_visible.is_visible = is_visible
    set_visible.is_visible = None

    visibility_ms = 1500
    visibility_time = visibility_ms if call_show else None

    mocker.patch.object(pygame.mouse, "set_visible", set_visible)

    game_display = GameDisplay(mockmedia(), dummy_font())
    game_display.key_bindings = {
        pygame.K_f: function_foo,
        pygame.K_b: function_bar
        }
    game_display.status = GameDisplay.RUNNING

    def show_mouse(time):
        show_mouse.time = time
    show_mouse.time = None

    mocker.patch.object(GameDisplay, "_GameDisplay__show_mouse_temporarily",
                        show_mouse)

    mocker.patch.object(gamedisplay.settings, "mouse_visibility_time",
                        visibility_ms/1000)

    event_handled = game_display.handle_event(event)
    assert isinstance(event_handled, bool)
    assert event_handled == handled
    assert function_foo_called == call_foo
    assert function_bar_called == call_bar
    assert set_visible.is_visible == call_is_visible
    assert show_mouse.time == visibility_time
    assert game_display.status == status
# pylint: enable=too-many-arguments
# pylint: enable=too-many-locals


def test_screenshot(mocker, mockmedia, dummy_font):
    """
    Test GameDisplay.__screenshot
    """
    game_display = GameDisplay(mockmedia(), dummy_font())

    def mocksave(surface, filename):
        mocksave.surface = surface
        mocksave.filename = filename

    mockfile = "dummy"

    mocker.patch.object(pygame.image, "save", mocksave)
    mocker.patch.object(gamedisplay.settings, "screenshot_file", mockfile)

    game_display._GameDisplay__screenshot()

    assert mocksave.surface is game_display.media.get_screen()
    assert mocksave.filename == mockfile


def test_ready_to_quit(mockmedia, dummy_font):
    """
    Test GameDisplay.ready_to_quit
    """
    game_display = GameDisplay(mockmedia(), dummy_font())

    assert game_display.ready_to_quit()

execute_data = [
    [ [ pygame.event.Event(pygame.QUIT, quit=GameDisplay.TERMINATE) ] ],
    [ [], [ pygame.event.Event(pygame.QUIT, quit=GameDisplay.TERMINATE) ] ],
    [ [ pygame.event.Event(pygame.KEYDOWN, key=pygame.K_x) ],
        [ pygame.event.Event(pygame.QUIT, quit=GameDisplay.TERMINATE) ] ],
    [ [ pygame.event.Event(pygame.KEYDOWN, key=pygame.K_x) ],
      [ pygame.event.Event(pygame.KEYDOWN, key=pygame.K_x),
        pygame.event.Event(pygame.QUIT, quit=GameDisplay.QUIT) ] ],
    ]


# pylint: disable=too-many-locals
@pytest.mark.parametrize("event_queue", execute_data)
def test_execute(event_queue, mocker, mockmedia, dummy_font):
    """
    Test GameDisplay.execute
    """
    game_display = GameDisplay(mockmedia(), dummy_font())

    expected_result = None

    expected_call_sequence = []
    for events in event_queue:
        expected_call_sequence.append(("draw",))
        expected_call_sequence.append(("tick"))
        for event in events:
            expected_call_sequence.append(("handle_event", event))
            if hasattr(event, 'quit'):
                expected_result = event.quit
        expected_call_sequence.append(("update_state",))

    call_sequence = []

    def mock_draw():
        nonlocal call_sequence
        call_sequence.append(("draw",))

    game_display.draw = mock_draw

    def mock_handle_event(event):
        nonlocal call_sequence
        call_sequence.append(("handle_event", event))
        if hasattr(event, 'quit'):
            game_display.status = event.quit
        return True

    game_display.handle_event = mock_handle_event

    def mock_update_state():
        nonlocal call_sequence
        call_sequence.append(("update_state",))

    game_display.update_state = mock_update_state

    def mock_get_events():
        nonlocal event_queue
        events = event_queue[0]
        event_queue = event_queue[1:]
        return events

    mocker.patch.object(pygame.event, "get", mock_get_events)

    def tick():
        call_sequence.append(("tick"))

    tick.old = game_display.media.tick
    game_display.media.tick = tick

    result = game_display.execute()

    assert result == expected_result
    assert call_sequence == expected_call_sequence


def test_quit(mockmedia, dummy_font):
    """
    Test GameDisplay.quit
    """
    game_display = GameDisplay(mockmedia(), dummy_font())

    game_display.quit(GameDisplay.TERMINATE)
    assert game_display.status == GameDisplay.TERMINATE

    game_display.quit(GameDisplay.QUIT)
    assert game_display.status == GameDisplay.QUIT


terminated_tests = [
    (GameDisplay.INITIALIZED, False),
    (GameDisplay.RUNNING, False),
    (GameDisplay.QUIT, False),
    (GameDisplay.TERMINATE, True)
    ]

@pytest.mark.parametrize("status, expected", terminated_tests)
def test_terminated(status, expected, mockmedia, dummy_font):
    """
    Test GameDisplay.terminated
    """
    game_display = GameDisplay(mockmedia(), dummy_font())

    game_display.status = status
    result = game_display.terminated()
    assert result == expected


def test_show_mouse_temporarily(mocker):
    """
    Test GameDisplay.__show_mouse_temporarily
    """
    def set_visible(is_visible):
        set_visible.is_visible = is_visible
    set_visible.is_visible = None

    mocker.patch.object(pygame.mouse, "set_visible", set_visible)

    def set_timer(event, millis, loops=0):
        set_timer.args = { "event": event, "millis": millis, "loops": loops }
    set_timer.args = None

    mocker.patch.object(pygame.time, "set_timer", set_timer)

    time = 420815

    GameDisplay._GameDisplay__show_mouse_temporarily(time)

    expected_timer_args = {
        "event": pygame.event.Event(pygame.USEREVENT,
                                    event=GameDisplay.EVENT_HIDE_MOUSE),
        "millis": time,
        "loops": 1
        }

    assert set_visible.is_visible
    assert set_timer.args == expected_timer_args
