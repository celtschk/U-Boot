# U-Boot
A simple game

![Screenshot](U-Boot-screenshot-1.png)

## Introduction

U-Boot is a simple game in which you gain score by destroying
submarines with bombs dropped from a ship. The game's title is
German for “submarine”. However, except fot the title, the game
is currently in English. But I eventually want to add
internationalization.

The main reason why I wrote this game is to gain familiarity
with Python.

## Playing the game

To play the game, make sure you've got a sufficient recent version
of Python and the required libraries installed (see file
dependencies.txt for details). Then run `python U-Boot.py`
(or possibly `python3 U-Boot.py`) in the main directory.

## About the code

The game is implemented in Python using the library pygame.

See file dependencies.txt to see what Python and library versions
I've tested it. Later versions should probably work, too. Earlier
versions may or may not work. Note that some early 2.x versions
of pygame had broken mp3 support on Linux; this game won't run
unter Linux with those versions.

Note that I've tested this game onLinux Mint both with native Python
and under Wine; it should therefore run both under Linux and Windows.
I didn't test it on MacOS, but I expect it to work there as well.

This game uses some artwork files from others. All of them are either
public domain or under a Creative Commons license. Please see
the file non_original_files.txt for details.

## Caveats

As the game is still in development, the save file format may change
at any commit, invalidating earlier saved games.
