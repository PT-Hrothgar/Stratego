from stratego.colors import Colors, pygame

SQUARE_SIZE = 80


class Square:
    NORMAL = Colors.DULL_GREEN
    ACTIVE = Colors.GREEN
    STRIKE = Colors.RED
    SELECTED = Colors.LIGHT_BLUE

    def __init__(self, /, display):
        if not isinstance(display, pygame.surface.Surface):
            msg = f"Expected pygame.surface.Surface object, got {display!r}"
            raise ValueError(msg)
        self.display = display
        self.display_width = display.get_width()
        self.display_height = display.get_height()
        self.gridx = Square.x
        self.gridy = Square.y
        self.lake = False
        self.selected = False
        self.state = Square.NORMAL
        Square.x += 1
        if Square.x == 11:
            Square.y += 1
            Square.x = 1
        self.x = self.display_width/2 + (SQUARE_SIZE + 2)*(self.gridx - 6) + 1
        self.y = self.display_height/2 + (SQUARE_SIZE + 2)*(self.gridy - 6) + 1

    def render(self, /, mode=NORMAL):
        if mode not in (Square.NORMAL, Square.ACTIVE, Square.STRIKE):
            raise ValueError("Square.render() expected Square.NORMAL, Square."
                             f"ACTIVE, or Square.STRIKE, got {mode!r}")

        if self.selected: mode = Square.SELECTED
        self.state = mode
        pygame.draw.rect(self.display, mode,
                         (self.x, self.y, SQUARE_SIZE, SQUARE_SIZE))

    def hovered(self, /):
        mouse = pygame.mouse.get_pos()
        return (self.x + SQUARE_SIZE > mouse[0] > self.x
                and self.y + SQUARE_SIZE > mouse[1] > self.y)

    def get_coords(self, /) -> tuple:
        return self.x, self.y, self.gridx, self.gridy

    def __str__(self, /):
        return f"<{self.x}, {self.y}, {self.gridx}, {self.gridy}>"


class Board:
    FRONT = 0
    BACK = 1

    @staticmethod
    def reset():
        Square.x = 1
        Square.y = 1

    def __init__(self, /, display):
        self.display = display
        self.squares = []
        self.centerx = self.display.get_width() / 2
        self.centery = self.display.get_height() / 2
        self.x = self.centerx - (SQUARE_SIZE*5 + 9)
        self.y = self.centery - (SQUARE_SIZE*5 + 9)
        self.totalsize = SQUARE_SIZE * 10 + 18
        self.CONSTANT = (self.display.get_width() - self.totalsize) / 2
        for counter in range(100):
            new = Square(display)
            if new.gridy in (5, 6) and new.gridx in (3, 4, 7, 8):
                new.lake = True
            new.render()
            self.squares.append(new)

    def render(self, /):
        pygame.draw.rect(self.display, Colors.BLACK,
                         (self.x, self.y, self.totalsize, self.totalsize))
        for square in self.squares:
            square.render()
        # Draw two lakes
        pygame.draw.circle(self.display, Colors.DARK_BLUE,
                           (self.centerx - (SQUARE_SIZE*2 + 4),
                            self.centery), SQUARE_SIZE + 1)
        pygame.draw.circle(self.display, Colors.DARK_BLUE,
                           (self.centerx + SQUARE_SIZE*2 + 4,
                            self.centery), SQUARE_SIZE + 1)

    def setsquare(self, /, squarex, squarey, mode):
        if mode not in (Square.NORMAL, Square.ACTIVE, Square.STRIKE):
            raise ValueError("Board.setsquare() expected Square.NORMAL, Square"
                             f".ACTIVE, or Square.STRIKE, got {mode!r}")
        if squarex not in range(1, 11):
            raise ValueError(f"No square with x coordinate of {squarex!r}")
        if squarey not in range(1, 11):
            raise ValueError(f"No square with y coordinate of {squarey!r}")
        square_index = (squarey - 1) * 10 + squarex - 1
        self.squares[square_index].render(mode)

    def get_square(self, /, squarex, squarey):
        if squarex not in range(1, 11):
            raise ValueError(f"No square with x coordinate of {squarex!r}")
        if squarey not in range(1, 11):
            raise ValueError(f"No square with y coordinate of {squarey!r}")
        square_index = (squarey - 1) * 10 + squarex - 1
        return self.squares[square_index]

    def get_starting_squares(self, /, section):
        if section not in (Board.FRONT, Board.BACK):
            raise ValueError("Board.get_starting_squares() expected either "
                             f"Board.FRONT or Board.BACK, got {section!r}")
        squares = []
        yrange = range(6, 10) if section == Board.FRONT else range(0, 4)
        for x in range(0, 10):
            for y in yrange:
                squares.append((x, y))
        return [self.squares[y*10 + x] for (x, y) in squares]
