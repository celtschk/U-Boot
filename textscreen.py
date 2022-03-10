#  Copyright 2022 Christopher Eltschka
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""
This module provides a class to display running text
"""

import pygame

import settings
import resources

from gamedisplay import GameDisplay

class TextScreen(GameDisplay):
    """
    Display a text in screenfuls.
    """
    def __init__(self, game, text):
        """
        Initialize the TextScreen object, paginating
        """
        super().__init__(game)

        # the colours used
        self.colours = {
            "foreground": resources.get_colour("paginated text"),
            "background": resources.get_colour("paginated background"),
            "footer":     resources.get_colour("paginated footer"),
            "error":      resources.get_colour("invalid control sequence")
            }

        self.layout = settings.paginate_layout
        self.font = self.game.paginated_font

        # paginate the text
        self.paginate(text)

        # start with the first page
        self.current_page = 0

        self.key_bindings.update({
            pygame.K_UP:        self.previous_page,
            pygame.K_PAGEUP:    self.previous_page,
            pygame.K_BACKSPACE: self.previous_page,
            pygame.K_DOWN:      self.next_page,
            pygame.K_PAGEDOWN:  self.next_page,
            pygame.K_SPACE:     self.next_page,
            pygame.K_HOME:      self.first_page,
            pygame.K_END:       self.last_page,
            pygame.K_q:         self.quit
            })


    def paginate(self, text):
        """
        The text is given as string ccontaining control sequences. A
        control sequence has the form @control@. Unknown control
        sequences are replaced by three red question marks.

        Currently, no control sequences are implemented.

        Multiple empty lines are combined to a single empty line.

        Additionally, the control characters line feed (\\n) and form feed
        (\\f) are interpreted.
        """
        # get the screen
        screen = self.game.screen
        screenwidth = screen.get_width()
        screenheight = screen.get_height()

        # calculate some useful values
        top = self.layout["border"]["top"]
        bottom = screenheight - self.layout["border"]["bottom"]
        left = self.layout["border"]["left"]
        right = screenwidth - self.layout["border"]["right"]

        linespacing = self.layout["line spacing"]

        textwidth = right - left

        line_height = self.font.size("")[1]

        # List of text pages. Each page itself is a pygame surface.
        # Initially the list is empty.
        self.pages = []

        # helper function to create an empty page
        def newpage():
            #page = pygame.Surface((screenwidth, screenheight))
            #page.fill(self.colours["background"])
            #return page
            return TextArea((textwidth, bottom - top),
                            self.colours["background"],
                            self.font, linespacing)

        # invalid control sequence sign. Always the same, thus
        # rendered exactly once
        invalid_control = self.font.render("???", True, self.colours["error"])

        # do the pagination
        for block in text.split("\f"):
            current_page = newpage()

            at_beginning_of_page = True

            # empty lines at the beginning of a page are ignored
            ignore_empty = True
            for line in block.split("\n"):
                # ignore empty lines where apropriate:
                if line == "":
                    if ignore_empty:
                        continue
                    # after an empty line, subsequent empty lines are ignored
                    ignore_empty = True
                else:
                    # don't ignore empty lines after non-empty ones
                    ignore_empty = False

                index = 0
                while index != len(line):
                    if line[index] == "@":
                        control_end = line.find("@", index+1)
                        if control_end == -1:
                            # unterminated control
                            control_name = None
                            index = len(line)
                        else:
                            control_name = line[index+1:control_end]
                            index = control_end + 1

                        if control_name is None:
                            item = invalid_control
                        elif control_name[:4] == "img ":
                            item = resources.load_image(control_name[4:])
                        elif control_name == "title":
                            item = self.font.render(
                                settings.game_title,
                                True,
                                self.colours["foreground"])
                        else:
                            item = invalid_control

                        current_page.render(item)
                    else:
                        left_index, right_index = index, line.find("@", index)
                        if right_index == -1:
                            right_index = len(line)

                        index = current_page.word_wrap(
                            line, index, right_index,
                            self.colours["foreground"])

                        if index != right_index:
                            pages.append(current_page)
                            current_page = newpage()

                    # if we get here, we're no longer at the beginning
                    # of the page
                    at_beginning_of_page = False

                # finally, move to a new line, unless at the beginning
                # of a page
                if not at_beginning_of_page:
                    current_page.line_feed()

            # commit the last page, if not empty
            if not at_beginning_of_page:
                self.pages += [current_page]


    def draw(self):
        """
        Draw the current page
        """
        screen = self.game.screen
        screen.fill(self.colours["background"])
        screen.blit(self.pages[self.current_page],
                    (self.layout["border"]["left"],
                     self.layout["border"]["top"]))

        text = self.font.render(
            f"Page {self.current_page+1} of {len(self.pages)}. "
            + "Up/Down: turn page, Q: back to menu.",
            True,
            self.colours["footer"])
        posx = self.layout["border"]["left"]
        posy = (self.game.screen.get_height()
                - self.layout["border"]["bottom"]
                + 10)
        self.game.screen.blit(text, (posx, posy))
        pygame.display.flip()


    def previous_page(self):
        """
        Move to the previous page
        """
        if self.current_page > 0:
            self.current_page -= 1


    def next_page(self):
        """
        Move to the next page
        """
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1


    def first_page(self):
        """
        Move to the first page
        """
        self.current_page = 0


    def last_page(self):
        """
        Move to the last page
        """
        self.current_page = len(self.pages) - 1


class TextArea(pygame.Surface):
    """
    This class represents a rectanglular area that contains running
    text.
    """
    def __init__(self, size, bg_colour, font, linespacing):
        width, height = size
        super().__init__((width, height))
        self.font = font
        self.linespacing = linespacing

        self.line_height = font.size("")[1]

        self.fill(bg_colour)

        self.hpos = 0
        self.vpos = 0


    def line_feed(self):
        """
        Goes to the next line. Returns whether that line fits.
        """
        self.hpos = 0
        self.vpos += self.linespacing

        return self.vpos + self.line_height < self.get_height()


    def get_item_width(self, item):
        """
        Gives the width of an item, which is either a string or a
        surface
        """
        if isinstance(item, str):
            return self.font.size(item)[0]
        return item.get_width()


    def fits_in_line(self, item_width):
        """
        Test whether an item of given width fits into the current line
        """
        return self.hpos + item_width <= self.get_width()


    def render(self, item, colour = None):
        """
        Render an item, if possible. The item can be a string or a
        surface. Returns whether the item was rendered. If it is a
        string, the colour must be given.

        If the item fits into the current line, it is appended to it.
        Otherwise, if a new line fits in the text area, render the
        item in the next line. Otherwise, give up.
        """
        item_width = self.get_item_width(item)

        if not self.fits_in_line(item_width):
            line_fits = self.line_feed()
            if not line_fits:
                return False

        if isinstance(item, str):
            surface = self.font.render(item, True, colour)
        else:
            surface = item

        self.blit(surface, (self.hpos, self.vpos))
        self.hpos += item_width
        return True


    def word_wrap(self, text, start, end, colour):
        """
        Word wrap text starting from index start until index end, or
        until the text area is full, whichever happens first.

        Returns the index up to which the text was rendered.
        """
        chunk_start = start

        def fits(chunk_end):
            return self.fits_in_line(
                self.get_item_width(text[chunk_start:chunk_end]))

        while chunk_start != end:
            if fits(end):
                result = self.render(text[chunk_start:end], colour)
                if not result:
                    return chunk_start
                return end

            chunk_end = resources.bisect(chunk_start, end, fits)

            last_space = text.rfind(" ", chunk_start, chunk_end)
            if last_space != -1:
                chunk_end = last_space

            result = self.render(text[chunk_start:chunk_end], colour)
            if not result:
                return chunk_start

            chunk_start = chunk_end
            if last_space != -1:
                self.line_feed()
                chunk_start += 1

        return end


    def at_beginning(self):
        return self.hpos == 0 and self.vpos == 0
