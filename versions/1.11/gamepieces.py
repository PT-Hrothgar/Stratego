from stratego.images import pygame, lighten_image, get_gamepiece_imgs, flip_img
from stratego.backend import GAMEPIECE_WIDTH, GAMEPIECE_HEIGHT, DEFAULT_FONT
from stratego.boards import SQUARE_SIZE

class Gamepiece:
    """Gamepiece class for Stratego game."""
    CREATED = 0
    ACTIVE = 1
    KILLED = 2

    LIGHTENED = 0
    NORMAL = 1
    BACK_VIEW = 2

    id = 0
    numbers = 1, 1, 2, 3, 4, 4, 4, 5, 8, 1, 6, 1
    ranks = {"Marshall": 1, "General": 2, "Colonel": 3, "Major": 4,
             "Captain": 5, "Lieutenant": 6, "Sergeant": 7, "Miner": 8,
             "Scout": 9, "Spy": "Spy", "Bomb": "Bomb", "Flag": "Flag"}

    def __init__(self, imgname, name, display, color, /):
        self.img = pygame.image.load(imgname)
        self.filename = imgname
        self.state = Gamepiece.CREATED
        self.name = name
        self.display = display
        self.color = color
        self.x_pos = None
        self.y_pos = None
        self.gridx = None
        self.gridy = None
        self.initalx = None
        self.initialy = None
        self.id = Gamepiece.id
        self.rank = Gamepiece.ranks[self.name]
        Gamepiece.id += 1

        id = self.id % 40
        try:
            index = [0, 1, 2, 4, 7, 11, 15, 19, 24, 32, 33, 39].index(id)
        except ValueError:
            self.representative = 0
        else:
            # Each player has one gamepiece from each rank
            # (Marshall, General, etc.) that is a "representative."
            self.representative = Gamepiece.numbers[index]


    def assert_active(self, /):
        """Make sure that ``self`` is an active piece."""
        if self.state != Gamepiece.ACTIVE:
            raise RuntimeError("Gamepiece is not active.")

    def get_pos(self, /) -> tuple:
        self.assert_active()
        return self.x_pos, self.y_pos, self.gridx, self.gridy

    def get_actual_pos(self, /, x, y) -> tuple:
        actualx = int(x + (SQUARE_SIZE - GAMEPIECE_WIDTH) / 2)
        actualy = int(y + (SQUARE_SIZE - GAMEPIECE_HEIGHT) / 2)
        return actualx, actualy

    def get_pic(self, /, lightened: bool = False):
        """
        Return an image of ``self``.

        Parameter
        ---------
        lightened: bool = False
            Decides whether to "lighten" (reduce the saturation of) the
            piece's image before returning it.
        """
        if lightened:
            return lighten_image(self.filename)
        else:
            return self.img

    def show_orig_pos(self, /):
        x, y = self.get_actual_pos(self.initialx, self.initialy)
        match self.state:
            case Gamepiece.ACTIVE:
                self.display.blit(self.img, (x, y))
            case Gamepiece.KILLED:
                self.display.blit(self.get_pic(lightened=True), (x, y))
            case _:
                raise ValueError("Gamepiece has not been activated.")

    def render(self, /, view=NORMAL):
        """
        Draw self to self.display.

        Parameter
        ---------
        view=Gamepiece.NORMAL
            Decides how to render ``self``. Default to Gamepiece.NORMAL,
            so that the normal image will be displayed. But it can also
            be Gamepiece.LIGHTENED, to display a lightened image (for if
            the gamepiece is killed, etc.), or Gamepiece.BACK_VIEW, to
            show the piece's "back". This will just show a rectangle.
        """
        self.assert_active()
        actual_x, actual_y = self.get_actual_pos(self.x_pos, self.y_pos)

        match view:
            case Gamepiece.NORMAL:
                self.display.blit(self.img, (actual_x, actual_y))
            case Gamepiece.LIGHTENED:
                self.display.blit(self.get_pic(lightened=True),
                                  (actual_x, actual_y))
            case Gamepiece.BACK_VIEW:
                pygame.draw.rect(self.display, self.color,
                                 (actual_x, actual_y,
                                  GAMEPIECE_WIDTH, GAMEPIECE_HEIGHT))
            case _:
                raise ValueError("Gamepiece.render() expected view of 0, 1, or "
                                 "2 for lightened, normal, or backside, got "
                                 f"{view}")

    def move(self, /, end_square, player1, player2, backside: bool = False):
        self.assert_active()
        end_x, end_y, end_gridx, end_gridy = end_square.get_coords()

        # We cannot move diagonally - make that known:
        if end_x != self.x_pos and end_y != self.y_pos:
            msg = "Gamepiece object cannot move diagonally"
            raise RuntimeError(msg)
        # But we have to be able to move in one direction!
        if end_x == self.x_pos and end_y == self.y_pos:
            msg = "Gamepiece.move() was called with no movement specified"
            raise RuntimeError(msg)

        if end_x != self.x_pos:
            increment = 1 if end_x > self.x_pos else -1
            def adjust_coord():
                self.x_pos += increment
            def done_moving():
                return self.x_pos == end_x

        elif end_y != self.y_pos:
            increment = 1 if end_y > self.y_pos else -1
            def adjust_coord():
                self.y_pos += increment
            def done_moving():
                return self.y_pos == end_y

        view = Gamepiece.BACK_VIEW if backside else Gamepiece.NORMAL

        # Set up a game loop:
        while not done_moving():
            for event in pygame.event.get():
                # Why don't we handle events here? Well, we don't
                # currently have an easy way to, for example, show the
                # gamepiece log from gamepieces.py, and besides, it
                # really isn't that big of a deal. This movement will
                # only take a little time, and the user can just wait
                # until it is over.
                pass
            adjust_coord()
            player1.board.render()
            player2.render_pieces(view=Gamepiece.BACK_VIEW)
            player1.render_pieces(view=view)
            pygame.display.update()
            pygame.time.wait(12)

        self.gridx = end_gridx
        self.gridy = end_gridy

    def get_open_squares(self, /, player, opponent):
        if self.name == "Scout":
            return self.get_scout_squares(player, opponent)
        else:
            return self.get_squares(player)

    def get_scout_squares(self, /, player, opnt):
        forbidden_square = self.get_forbidden_square(player.last_two_moves)
        def fix(row):
            blocked = False
            old_row = row.copy()
            for square in old_row:
                if player.is_square_occupied(square):
                    blocked = True
                if player.board.get_square(*square).lake:
                    blocked = True
                if blocked or square == forbidden_square:
                    row.remove(square)
                if opnt.is_square_occupied(square):
                    blocked = True
            return row

        left_row = fix([(x, self.gridy) for x in range(self.gridx-1, 0, -1)])
        right_row = fix([(x, self.gridy) for x in range(self.gridx+1, 11)])
        top_col = fix([(self.gridx, y) for y in range(self.gridy-1, 0, -1)])
        bottom_col = fix([(self.gridx, y) for y in range(self.gridy+1, 11)])
        return left_row + right_row + top_col + bottom_col

    def get_squares(self, /, player):
        self.assert_active()
        if self.name in ("Bomb", "Flag"):
            return []
        squares = []
        forbidden_square = self.get_forbidden_square(player.last_two_moves)

        def process_coords(coords):
            nonlocal squares
            square = player.board.get_square(*coords)
            if (not player.is_square_occupied(coords) and not square.lake
                    and coords != forbidden_square):
                squares.append(coords)

        if self.gridx != 1:
            coords = self.gridx - 1, self.gridy
            process_coords(coords)
        if self.gridx != 10:
            coords = self.gridx + 1, self.gridy
            process_coords(coords)
        if self.gridy != 1:
            coords = self.gridx, self.gridy - 1
            process_coords(coords)
        if self.gridy != 10:
            coords = self.gridx, self.gridy + 1
            process_coords(coords)
        return squares

    def hovered(self, /):
        mouse = pygame.mouse.get_pos()
        return (self.x_pos + SQUARE_SIZE > mouse[0] > self.x_pos
                and self.y_pos + SQUARE_SIZE > mouse[1] > self.y_pos)

    def inverted_image(self, /):
        return flip_img(self.filename)

    def get_name(self, /, font_size=20):
        """
        Return a text object with the piece's name written in its color, in
        the supplied font size.
        """
        try:
            font_size = int(font_size)
        except ValueError as e:
            raise ValueError("Gamepiece.get_name() expected int-like object, "
                             f"got {font_size!r}") from e
        font = pygame.font.SysFont(DEFAULT_FONT, font_size)
        return font.render(self.name, True, self.color)

    def die(self, /):
        self.x_pos = None
        self.y_pos = None
        self.gridx = None
        self.gridy = None
        self.state = Gamepiece.KILLED

    def get_forbidden_square(self, /, last_two_moves):
        if all(last_two_moves):
            if (last_two_moves[0][0] == last_two_moves[1][1]
                    == (self.gridx, self.gridy) and last_two_moves[0][1]
                    == last_two_moves[1][0]):
                return last_two_moves[0][1]
        return None

    @staticmethod
    def get_gamepieces(color, id, display, /) -> list:
        """
        Return a list of ``stratego.gamepieces.Gamepiece`` objects in
        the given color.
        """
        gamepiece_list = []
        name_list = (["Marshall"] + ["General"] + ["Colonel"]*2 + ["Major"]*3
                     + ["Captain"]*4 + ["Lieutenant"]*4 + ["Sergeant"]*4
                     + ["Miner"]*5 + ["Scout"]*8 + ["Spy"] + ["Bomb"]*6
                     + ["Flag"])
        imgname_list = get_gamepiece_imgs(color, id)
        ml, gl, cl, mjr, cn, lt, sgt, mnr, sct, sy, bb, fg = imgname_list
        imgname_list = ([ml] + [gl] + [cl]*2 + [mjr]*3 + [cn]*4 + [lt]*4
                          + [sgt]*4 + [mnr]*5 + [sct]*8 + [sy] + [bb]*6 + [fg])
        for imgname, name in zip(imgname_list, name_list):
            gamepiece_list.append(Gamepiece(imgname, name, display, color))

        return gamepiece_list
