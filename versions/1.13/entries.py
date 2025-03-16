from stratego.colors import Colors, pygame
from stratego.backend import DEFAULT_FONT


class Entry:
    """
    Powerful and easy-to-use entry fields.

    Parameters
    ----------
    display:
        The entry field's surface to draw onto. Must be ``pygame.Surface``
        object.
    x, y:
        Coordinates for the upper left corner of the button on the display.
        Must be `int` objects.
    width, height:
        Width and height variables for the entry field. Must be `int`
        objects.
    x_deficit=0, y_deficit=0:
        If the ``display`` parameter is a Surface that is not the main
        display, set these parameters to the x and y values at which
        ``display`` will be drawn onto the main display - in other words,
        the distances in the x and y directions that ``display`` will be
        from the edges. Must be `int` objects.

    Example:
    --------
    >>> myentry = Entry(game_display, 100, 100, 400, 50)

    How to use the ``Entry`` class
    ------------------------------
    1. Create and render your entry fields:
    >>> entry1 = Entry(*entryargs1)
    >>> entry2 = Entry(*entryargs2)
    >>> entry1.render()
    >>> entry2.render()
    2. In the game loop, pass each event to Entry.process_event():
    >>> while True:
    ...     for event in pygame.event.get():
    ...         if event.type == pygame.QUIT:
    ...             exitgame()
    ...         ...
    ...         # After processing events normally, pass them to this function:
    ...         entry1.process_event(event)
    ...         entry2.process_event(event)
    3. Use Entry.update() to see if Return was pressed:
    ...     if entry1.update():
    ...         print("Result of entry1:", entry1.text)
    ...     if entry2.update():
    ...         print("Result of entry2:", entry2.text)
    """
    def __init__(self, /, display, x, y, width, height, x_deficit=0,
                 y_deficit=0):
        msg = ("Invalid ``{}`` argument for Entry.__init__(); "
               + "see Entry.__doc__ for more information.")
        if not isinstance(display, pygame.surface.Surface):
            raise ValueError(msg.format("display"))
        if not isinstance(x, int):
            raise ValueError(msg.format("x"))
        if not isinstance(y, int):
            raise ValueError(msg.format("y"))
        if not isinstance(width, int):
            raise ValueError(msg.format("width"))
        if not isinstance(height, int):
            raise ValueError(msg.format("height"))
        if not isinstance(x_deficit, int):
            raise ValueError(msg.format("x_deficit"))
        if not isinstance(y_deficit, int):
            raise ValueError(msg.format("y_deficit"))

        self.display = display
        self.backspace = False
        self.active = False
        self.complete = False
        self.control_pressed = False
        self.paste = False
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.x_deficit = x_deficit
        self.y_deficit = y_deficit
        self.active_char = ''
        self.count = 0
        self.text = ''
        self.font = font = pygame.font.SysFont(DEFAULT_FONT, self.height-10)

    def render(self, /, show_text=True):
        """
        Draw self to self.display.

        Entry.render() will draw the entry field's white area with a 1px
        border to self.display, using the specified x, y, width, and
        height data. If ``self.active`` is True, the border will be
        black, for Active, and if False, the border will be light gray
        for Inactive.

        Unless ``show_text`` is set to False, Entry.render() will also
        write self.text into the field, with a 2px border between it and
        the edge of the white area.
        This function will NOT update the display in any way.
        """
        if self.active:
            # Black border = Active
            border_color = Colors.BLACK
        else:
            # Light gray border = Inactive
            border_color = Colors.LIGHT_GRAY

        pygame.draw.rect(self.display, border_color,
                         (self.x, self.y, self.width, self.height))
        # This second box is the white box inside the "border box", which
        # was entirely the color of the input field's border. This one is
        # slightly smaller: it leaves a 1px border all around.
        pygame.draw.rect(self.display, Colors.WHITE,
                         (self.x+1, self.y+1, self.width-2, self.height-2))
        if show_text:
            # Write the text back onto/"into" the field.
            text_obj = self.font.render(self.text, True, Colors.BLACK)
            # Leave an additional 2px "border" between the text itself and the
            # edge of the white box.
            self.display.blit(text_obj, (self.x+3, self.y+3))

    def validate_input_length(self, /, text_obj):
        """
        Ensure that a given text object is small enough to fit inside the
        entry field.
        """
        # The text object will be small enough to fit in the entry field if
        # and only if its width is, at most, 6 pixels less than the total
        # width of the field itself (allowing for both borders).
        return text_obj.get_rect().right <= self.width - 6

    def process_event(self, /, event):
        """
        Update the entry field's data based on a passed event.

        Call this function with each event returned by pygame.event.get()
        that may be a MOUSEBUTTONUP, KEYDOWN, or KEYUP event. The event will
        then be processed by `self` if it pertains to the entry field in any
        way.
        See Entry.__doc__ for examples of usage.
        This function will not draw changes to the display in any way;
        call self.update() to normally update on each iteration of the game
        loop.
        """
        if not isinstance(event, pygame.event.Event):
            raise ValueError("Entry.process_event() expected pygame.Event "
                             f"object, got {event!r}")
        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            x = pos[0] - self.x_deficit
            y = pos[1] - self.y_deficit
            if (self.x < x < self.x+self.width
                    and self.y < y < self.y+self.height):
                if not self.active:
                    self.active = True
                    self.render()
            else:
                if self.active:
                    self.active_char = ''
                    self.active = False
                    self.render()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.backspace = True
                self.active_char = ''
                return
            elif event.key == pygame.K_RETURN:
                self.complete = True
                return
            elif event.key in (pygame.K_LCTRL, pygame.K_RCTRL):
                self.control_pressed = True
                return
            elif event.key == pygame.K_v:
                if self.control_pressed:
                    self.paste = True
                    return
            letter = event.unicode
            if letter:
                if letter.isprintable():
                    self.active_char = letter
                    self.count = 0

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_BACKSPACE:
                self.backspace = False
                return
            elif event.key in (pygame.K_LCTRL, pygame.K_RCTRL):
                self.control_pressed = False
                return
            if event.unicode == self.active_char:
                self.active_char = ''

        elif event.type == pygame.TEXTINPUT:
            if self.active_char or self.backspace:
                self.count += 1

    def update(self, /):
        """
        Make all necessary changes to the entry field, especially writing
        new letters onto the end of existing text.

        If a key is held down for longer than normal, Entry.update() will
        continue adding the key's letter until it is released.
        This function will return True if Enter/Return was pressed,
        otherwise False.
        """
        if self.complete:
            return True

        if self.active:
            original_text = self.text
            # Add new letters
            self.text = ''.join((self.text, self.active_char * self.count))
            if self.paste:
                try:
                    clipboard = pygame.scrap.get(pygame.SCRAP_TEXT).decode()
                except AttributeError:
                    pass
                else:
                    clipboard = clipboard.replace("\0", "")
                    if clipboard:
                        self.text = ''.join((self.text, clipboard))
                        self.paste = False
            if self.backspace:
                self.text = self.text[:-1]
                # Overwrite longer text
                self.render(show_text=False)
                # Give the user a moment to release Backspace
                pygame.time.wait(130)
            if self.text != original_text:
                text_obj = self.font.render(self.text, True, Colors.BLACK)
                # Ensure that text can fit into field
                if self.validate_input_length(text_obj):
                    self.display.blit(text_obj, (self.x+3, self.y+3))
                else:
                    self.text = original_text

        self.count = 0
        return False
