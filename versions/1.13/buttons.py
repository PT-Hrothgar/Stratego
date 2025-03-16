from stratego.colors import pygame, Colors
from stratego.backend import DEFAULT_FONT


class Button:
    """
    Highly portable and easy-to-use buttons.

    ``Button`` provides utilities for creating:
        - Messages for buttons.
        - Positions, widths, and heights for buttons.
        - Two different colors for the buttons - one to normally show, and
          another to show when they are being hovered over.
        - Custom arguments and keyword arguments to pass to each button's
          function.
    And ``Button`` will also change the cursor to a "hand" whenever a button
    is being hovered over.

    Parameters
    ----------
    msg:
        The message to display on the button. It will be converted to a
        string and then centered on the button.
    x, y:
        Coordinates for the upper left corner of the button on the display.
        They will be converted to integers, if possible.
    width, height:
        Width and height variables for the button. They will be converted to
        integers, if possible.
    norm_color:
        The normal color for the button, to be used when it is not being
        hovered over. Must be RGB color in tuple form.
    hover_color:
        The color to be used for the button when it is being hovered over.
        Must be RGB color in tuple form.
    display:
        The button's game display. Must be ``pygame.Surface`` object.
    func=None:
        Callable object to be used for the button's function. Default blank
        function.
    args=():
        Positional arguments in tuple form to be passed to the button's
        function when it is clicked.
    kwargs={}:
        Keyword arguments in dictionary form to be passed to the button's
        function when it is clicked.
    x_deficit=0, y_deficit=0:
        If the ``display`` parameter is a Surface that is not the main
        display, set these parameters to the x and y values at which
        ``display`` will be drawn onto the main display - in other words,
        the distances in the x and y directions that ``display`` will be
        from the edges. They will be converted to integers, if possible.

    Example:
    --------
    >>> Button("Play Level 1", 150, 450, 100, 50, (0,200,0), (0,255,0),
    ...        game_display, play_game, kwargs={"level": 1})

    How to use the ``Button`` class
    -------------------------------
    1. Delete all buttons that have been created:
    >>> Button.clear_all_buttons()
    2. Create your buttons:
    >>> Button(*buttonargs1)
    >>> Button(*buttonargs2)
    3. Process MOUSEBUTTONUP event in game loop:
    >>> while True:
    ...     for event in pygame.event.get():
    ...         ...
    ...         if event.type == pygame.MOUSEBUTTONUP:
    ... #############################################
    ...             result = Button.process_click()
    ... #############################################
    When this function is called, ``Button`` will check to see if any
    buttons are being hovered over, and if one is (implying that the user
    clicked on it), ``Button`` will call its function with the supplied
    arguments and keyword arguments, and return the result.
    4. Call Button.listen() in game loop:
    >>> while True:
    ...     ...
    ...     Button.listen()
    This function checks to see if a button is being hovered over. If one
    is, it will change that button's color to the "hover_color", and change
    the cursor to a little hand.
    """
    buttons = []
    id = 0

    def __init__(self, /, txt, x, y, width, height, norm_color, hover_color,
            display, func=None, args=(), kwargs={}, x_deficit=0, y_deficit=0):
        # Check parameters.
        msg = ("Invalid ``{}`` argument for Button.__init__();"
               + " see help(Button) for more information")
        if not isinstance(args, tuple):
            raise ValueError(msg.format("args"))
        if not isinstance(kwargs, dict):
            raise ValueError(msg.format("kwargs"))
        if not isinstance(norm_color, tuple):
            raise ValueError(msg.format("norm_color"))
        if not isinstance(hover_color, tuple):
            raise ValueError(msg.format("hover_color"))
        if not isinstance(display, pygame.Surface):
            raise ValueError(msg.format("display"))

        if len(norm_color) not in (3, 4):
            raise ValueError(msg.format("norm_color"))
        if len(hover_color) not in (3, 4):
            raise ValueError(msg.format("hover_color"))

        try:
            x = int(x)
        except (TypeError, ValueError) as e:
            raise ValueError(msg.format("x")) from e
        try:
            y = int(y)
        except (TypeError, ValueError) as e:
            raise ValueError(msg.format("y")) from e
        try:
            width = int(width)
        except (TypeError, ValueError) as e:
            raise ValueError(msg.format("width")) from e
        try:
            height = int(height)
        except (TypeError, ValueError) as e:
            raise ValueError(msg.format("height")) from e
        try:
            x_deficit = int(x_deficit)
        except (TypeError, ValueError) as e:
            raise ValueError(msg.format("x_deficit")) from e
        try:
            y_deficit = int(y_deficit)
        except (TypeError, ValueError) as e:
            raise ValueError(msg.format("y_deficit")) from e

        # Were parameters supplied, but no function?
        if (not func) and any((args, kwargs)):
            msg = "Function parameters were supplied with no function"
            raise ValueError(msg)

        if func:
            if not callable(func):
                msg = ("Button.__init__() expected callable function, "
                       + f"got {func!r}")
                raise ValueError(msg)
            self.func = func

        else:
            def empty_func():
                pass
            self.func = empty_func

        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.x_deficit = x_deficit
        self.y_deficit = y_deficit
        self.norm_color = norm_color
        self.hover_color = hover_color
        self.display = display
        self.msg = str(txt)
        self.active = False
        self.args = args
        self.kwargs = kwargs
        self.id = Button.id
        Button.id += 1
        font_size = max(int(self.height/2), 10)
        self.font = pygame.font.SysFont(DEFAULT_FONT, font_size)

        self.render(norm_color)
        Button.buttons.append(self)

    def render(self, color, /):
        """
        Render the button to its display in the supplied color.

        Parameters
        ----------
        color: parameter-only, tuple
            An RGB color in tuple form.
        """
        pygame.draw.rect(self.display, color,
                         (self.x, self.y, self.width, self.height))
        text_surf = self.font.render(self.msg, True, Colors.BLACK)
        text_rect = text_surf.get_rect()
        text_rect.center = self.x + (self.width/2), self.y + (self.height/2)
        self.display.blit(text_surf, text_rect)

    def switch(self, /):
        """
        Switch the button's color - from its normal color to its color
        for when it is hovered over, or vice versa.
        """
        if self.active:
            color = self.norm_color
        else:
            color = self.hover_color
        self.render(color)
        self.active = not self.active

    def switch_text(self, /, new_msg):
        """
        Change the text on the button.
        """
        self.msg = new_msg
        if self.hovered():
            self.render(self.hover_color)
        else:
            self.render(self.norm_color)

    def hovered(self, /):
        """
        Return True if the button is being hovered over, otherwise
        return False.
        """
        mouse = pygame.mouse.get_pos()
        return (self.x + self.width > mouse[0] - self.x_deficit > self.x
                and self.y + self.height > mouse[1] - self.y_deficit > self.y)

    def destroy(self, /):
        """Delete the button from the system."""
        pygame.draw.rect(self.display, Colors.WHITE,
                         (self.x, self.y, self.width, self.height))
        for i in range(len(Button.buttons)):
            if Button.buttons[i].id == self.id:
                Button.buttons.pop(i)

    def __call__(self, /):
        """Call the button's function, with the supplied arguments."""
        return self.func(*self.args, **self.kwargs)

    @staticmethod
    def listen():
        """
        See if any buttons are being hovered over, or if any buttons
        that were being hovered over are now not, and act accordingly.

        This function will not update the display in any way.
        """
        for button in Button.buttons:
            if button.hovered():
                if not button.active:
                    button.switch()
                    # Turn the cursor into the little "hand":
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

            elif button.active:
                # The cursor left the button, so set it back to the
                # normal arrow:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                button.switch()

    @staticmethod
    def process_click():
        """
        Call the function of whatever Button instance is being hovered.

        Only call this function if there was a MOUSEBUTTONUP event. When
        it is called, this function will assume that the mouse was
        clicked. If no buttons are being hovered over, it will do
        nothing.
        """
        for button in Button.buttons:
            if button.hovered():
                # The button was clicked, so set the cursor back to the
                # normal arrow. (The button will probably subsequently be
                # destroyed.)
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                return button()

    @staticmethod
    def clear_all_buttons():
        """Destroy all buttons that were created."""
        Button.buttons = []
        Button.id = 0
