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
            pygame.K_q:         self.quit,
            pygame.K_ESCAPE:    self.quit
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
        # List of text pages. Each page itself is a pygame surface.
        # Initially the list is empty.
        self.pages = []

        # do the pagination
        for block in text.split("\f"):
            current_page = self.new_page()

            for line in block.split("\n"):
                index = 0
                while index != len(line):
                    if line[index] == "@":
                        control_end = line.find("@", index+1)
                        if control_end == -1:
                            # unterminated control, the "@invalid"
                            # string cannot be generated by any (valid
                            # or invalid) control sequence, therefore
                            # it is guaranteed to be invalid
                            self.render_control(current_page, "@invalid")
                            index = len(line)
                        else:
                            self.render_control(current_page,
                                                line[index+1:control_end])
                            index = control_end + 1

                    else:
                        right_index = line.find("@", index)
                        if right_index == -1:
                            right_index = len(line)

                        index = current_page.word_wrap(
                            line, index, right_index,
                            self.colours["foreground"])

                        if index != right_index:
                            self.pages.append(current_page)
                            current_page = self.new_page()

                # finally, move to a new line, unless at the beginning
                # of a page
                if not current_page.at_beginning():
                    current_page.line_feed()

            # commit the last page, if not empty
            if not current_page.at_beginning():
                self.pages += [current_page]


    def new_page(self):
        """
        create an empty page
        """
        screen = self.game.screen

        textwidth = (screen.get_width()
                     - self.layout["border"]["right"]
                     - self.layout["border"]["left"])

        textheight = (screen.get_height()
                      - self.layout["border"]["bottom"]
                      - self.layout["border"]["top"])

        return TextArea((textwidth, textheight),
                        self.colours["background"],
                        self.font,
                        self.layout["line spacing"])


    def render_control(self, current_page, control_name):
        """
        Render a control sequence
        """
        if control_name[:4] == "img ":
            item = resources.load_image(control_name[4:])
        elif control_name == "title":
            item = self.font.render(
                settings.game_info["title"],
                True,
                self.colours["foreground"])
        else:
            # invalid control
            item = self.font.render("???", True, self.colours["error"])

        current_page.render(item)



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

        # at the beginning of a page, don't do line feeds
        self.no_feed = True


    def line_feed(self):
        """
        Goes to the next line. Returns whether that line fits.
        """
        # ignore line feed requests where line feeds are unwanted
        if self.no_feed:
            return True

        # after an empty line, don't add another one
        if self.hpos == 0:
            self.no_feed = True

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

        # after rendering an item, a line feed should be honoured
        self.no_feed = False
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
                # since the omitted space may mean the next word now
                # fits, an explicit line feed is needed to prevent
                # adding the next word to the current line without
                # space
                self.line_feed()
                chunk_start += 1

        return end


    def at_beginning(self):
        """
        Return whether we are still at the beginning of the page
        """
        return self.hpos == 0 and self.vpos == 0
