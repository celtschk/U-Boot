import pygame
import settings

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
        self.fg_colour = settings.colours["paginated text"]
        self.bg_colour = settings.colours["paginated background"]
        self.err_colour = "red"

        self.layout = settings.paginate_layout
        self.font = self.game.paginated_font

        # paginate the text
        self.paginate(text)

        # start with the first page
        self.current_page = 0


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

        lines_per_page = (bottom - top)//linespacing
        textwidth = right - left

        line_height = self.font.size("")[1]

        # List of text pages. Each page itself is a pygame surface.
        # Initially the list is empty.
        self.pages = []

        # helper function to create an empty page
        def newpage():
            page = pygame.Surface((screenwidth, screenheight))
            page.fill(self.bg_colour)
            return page

        # invalid control sequence sign. Always the same, thus
        # rendered exactly once
        invalid_control = self.font.render("???", True, self.err_colour);
        
        # do the pagination
        for block in text.split("\f"):
            current_page = newpage()
            current_vpos = top
            current_hpos = left

            # helper function to do a line feed
            def line_feed():
                nonlocal current_vpos
                nonlocal current_hpos
                nonlocal current_page

                current_hpos = left
                current_vpos += linespacing

                # if the next line does not fit on the current page,
                # commit that page and start a new one
                if current_vpos + line_height > bottom:
                    self.pages += [current_page]
                    current_page = newpage()
                    current_vpos = top

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

                index = 0;
                while (index != len(line)):
                    remaining_width = textwidth - current_hpos
                        
                    if line[index] == "@":
                        control_end = line.find("@", index+1)
                        if control_end == -1:
                            # unterminated control
                            control_name = None
                            index = len(line)
                        else:
                            control_name = line[index+1:control_end]
                            index = control_end + 1

                        # currently all control sequences are invalid
                        if invalid_control.get_width() > remaining_width:
                            line_feed()
                        current_page.blit(invalid_control,
                                          (current_hpos, current_vpos))
                        current_hpos += invalid_control.get_width()
                    else:
                        left_index, right_index = index, line.find("@", index)
                        if right_index == -1:
                            right_index = len(line)

                        width = self.font.size(line[index:right_index])[0]
                        wrap_line = (width > remaining_width)
                        if not wrap_line:
                            # everything fits into one line
                            chunk_end = right_index
                            spacewrap = False
                        else:
                            # use binary search to find where to ideally
                            # wrap the line
                            while right_index - left_index > 1:
                                middle_index = (left_index + right_index) // 2
                                width = self.font.size(line[index:middle_index])[0]
                                if width > remaining_width:
                                    right_index = middle_index
                                else:
                                    left_index = middle_index

                            chunk_end = line.rfind(" ", index, right_index)
                            if chunk_end == -1:
                                chunk_end = right_index
                                spacewrap = False
                            else:
                                spacewrap = True

                        # render the text on the page
                        rendered_chunk = self.font.render(
                            line[index:chunk_end],
                            True,
                            self.fg_colour)
                        current_page.blit(rendered_chunk,
                                          (current_hpos, current_vpos))
                        current_hpos += rendered_chunk.get_width()

                        # continue rendering at chunk_end
                        index = chunk_end

                        # when wrapping on a space, that space is skipped
                        if spacewrap:
                            index += 1

                        # if word wrapped, add a line feed
                        if wrap_line:
                            line_feed()

                # finally, move to a new line
                line_feed()

            # commit the last page
            self.pages += [current_page]


    def draw(self):
        """
        Draw the current page
        """
        self.game.screen.blit(self.pages[self.current_page], (0, 0))
        pygame.display.flip()


    def handle_event(self, event):
        """
        Handle an event
        """
        if super().handle_event(event):
            return True

        if event.type == pygame.KEYDOWN:
            # Up, Backspace or Page Up go to the previous page
            if event.key in {pygame.K_UP,
                             pygame.K_BACKSPACE,
                             pygame.K_PAGEUP}:
                if self.current_page > 0:
                    self.current_page -= 1

            # Down, Space or Page Down go to the next page
            elif event.key in {pygame.K_DOWN,
                               pygame.K_SPACE,
                               pygame.K_PAGEDOWN}:
                if self.current_page < len(self.pages) - 1:
                    self.current_page += 1

            # Home goes to the first page
            elif event.key == pygame.K_HOME:
                self.current_page = 0

            # End goes to the last page
            elif event.key == pygame.K_END:
                self.current_page = len(self.pages) - 1

            # F toggles fullscreen display
            elif event.key == pygame.K_f:
                self.game.toggle_fullscreen()

            # Q quits the game and returns to the menu
            elif event.key == pygame.K_q:
                self.quit()
