from stratego.colors import pygame, Colors
from stratego.gamepieces import Gamepiece
from stratego.backend import (
    wait,
    center_text,
    exit_game,
    notify_about_click,
    EVENTS,
    DEFAULT_FONT
)
from stratego.entries import Entry
from stratego.buttons import Button
from stratego.boards import Board, Square
from stratego.game_loops import show_gamepiece_log, show_ranks, warn_to_leave
import random


class Player(Colors):
    """Player class for Stratego game."""
    @staticmethod
    def reset():
        Player.players_id = 0
        Player.colors = [Colors.PLAYER_RED, Colors.PLAYER_BLUE]
        random.shuffle(Player.colors)
        Board.reset()

    def __init__(self, /, display, board):
        if not isinstance(display, pygame.surface.Surface):
            msg = f"Expected pygame.surface.Surface object, got {display!r}"
            raise ValueError(msg)
        if not isinstance(board, Board):
            msg = f"Expected stratego.boards.Board object, got {board!r}"
            raise ValueError(msg)

        Player.players_id += 1
        self.id = Player.players_id
        self.display = display
        self.display_width = display.get_width()
        self.display_height = display.get_height()
        self.board = board
        self.victorious = False
        self.color = Player.colors.pop(0)
        if self.color == Colors.PLAYER_RED: self.boardsection = Board.FRONT
        else: self.boardsection = Board.BACK
        self.last_two_moves = None, None
        self.pieces = Gamepiece.get_gamepieces(self.color, self.id,
                                               self.display)

    def render_pieces(self, /, view=Gamepiece.NORMAL):
        if view not in (Gamepiece.NORMAL, Gamepiece.LIGHTENED,
                        Gamepiece.BACK_VIEW):
            raise ValueError("Player.render_pieces() expected value of 0, 1, "
                             "or 2 for lightened, normal, or backside, got "
                             f"{view}")
        for piece in self.pieces:
            if piece.state == Gamepiece.ACTIVE:
                piece.render(view=view)

    def get_name(self, /, forbidden_name=None):
        """
        Create text input area for the player to type in his name.

        Player.get_name() also creates a green button saying "Submit" as
        an alternative to the Return key, but neither will work until
        user has typed at least one character.
        The ``forbidden_name`` parameter is a name that the user is not
        allowed to use (for example, if his opponent already typed in a
        name, and identical names are not allowed).
        """
        if forbidden_name:
            forbidden_name = str(forbidden_name)
        font = pygame.font.SysFont(DEFAULT_FONT, 20)
        text = font.render(f"Player {self.id}, enter your name:", True,
                           Colors.BLACK)
        text_y = int(self.display_height/2 - 60)
        button_x = self.display_width/2 - 50
        button_y = self.display_height/2 + 50
        x_pos = int(self.display_width/2 - 175)
        y_pos = int(self.display_height/2 - 25)
        entry = Entry(self.display, x_pos, y_pos, 350, 50)
        entry.render()

        def render():
            self.display.fill(Colors.WHITE)
            entry.render()
            center_text(text, self.display, y=text_y)
            Button.clear_all_buttons()
            Button("Submit", button_x, button_y, 100, 50,
                   Colors.DULL_GREEN, Colors.GREEN, self.display,
                   notify_about_click, (True,))

        render()
        while True:
            for event in pygame.event.get():
                give_to_entry = True
                if event.type == pygame.QUIT:
                    exit_game()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        give_to_entry = False
                        if warn_to_leave(self.display):
                            exit_game()
                        else:
                            render()
                elif event.type == pygame.MOUSEBUTTONUP:
                    if Button.process_click():
                        entry.complete = True
                elif event.type in EVENTS:
                    render()
                if give_to_entry:
                    entry.process_event(event)

            entry.update()
            if entry.complete:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                if entry.text:
                    if entry.text != forbidden_name:
                        self.playername = entry.text
                        return
                    else:
                        font = pygame.font.SysFont(DEFAULT_FONT, 15)
                        text = font.render("That name's taken!", True,
                                           Colors.BLACK)
                        text_y = self.display_height/2 + 115
                        center_text(text, self.display, y=text_y)
                entry.complete = False
            Button.listen()
            pygame.display.update()
            pygame.time.wait(10)

    def setup(self, /):
        text_size = int(self.board.CONSTANT / 15)
        name = self.name(text_size, with_comma=True)
        rect = name.get_rect()
        x = self.board.x/2
        rect.centerx = x
        rect.centery = 30
        font = pygame.font.SysFont(DEFAULT_FONT, text_size)
        textlist = (
            font.render("set up your pieces!", True, Colors.BLACK),
            font.render("Select two pieces at a", True, Colors.BLACK),
            font.render("time to switch them.", True, Colors.BLACK),
        )
        squares = self.board.get_starting_squares(self.boardsection)
        for piece, square in zip(self.pieces, squares):
            coords = square.get_coords()
            piece.x_pos = coords[0]
            piece.y_pos = coords[1]
            piece.gridx = coords[2]
            piece.gridy = coords[3]
            piece.initialx = coords[0]
            piece.initialy = coords[1]
            piece.state = Gamepiece.ACTIVE

        def render():
            self.display.fill(Colors.WHITE)
            self.display.blit(name, rect)
            y = text_size/2 + 36
            for text in textlist:
                textrect = text.get_rect()
                textrect.centerx = x
                textrect.top = y
                self.display.blit(text, textrect)
                y += text_size + 6
            Button.clear_all_buttons()
            Button("Done!", x-50, self.display_height/2, 100, 50,
                     Colors.DULL_GREEN, Colors.GREEN, self.display,
                     notify_about_click, (True,))
            self.board.render()
            self.render_pieces()
        render()
        pieces_selected = []
        squares_selected = []
        done = False

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if warn_to_leave(self.display):
                            exit_game()
                        else:
                            render()
                    elif event.key == pygame.K_RETURN:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                        done = True
                    elif event.key == pygame.K_F1:
                        show_ranks(self.display, self)
                        render()
                elif event.type == pygame.MOUSEBUTTONUP:
                    for piece in self.pieces:
                        if piece.hovered():
                            for square in self.board.squares:
                                if square.get_coords() == piece.get_pos():
                                    squares_selected.append(square)
                                    square.selected = True
                                    square.render()
                            piece.render()
                            pieces_selected.append(piece)
                    if Button.process_click():
                        done = True
                elif event.type in EVENTS:
                    render()
            if len(squares_selected) == 2:
                for square in squares_selected:
                    square.selected = False
                    square.render()
                piece1 = pieces_selected[0]
                piece2 = pieces_selected[1]
                piece1_old_coords = piece1.get_pos()
                piece2_old_coords = piece2.get_pos()
                piece1.x_pos = piece2_old_coords[0]
                piece1.y_pos = piece2_old_coords[1]
                piece1.gridx = piece2_old_coords[2]
                piece1.gridy = piece2_old_coords[3]
                piece1.render()
                piece2.x_pos = piece1_old_coords[0]
                piece2.y_pos = piece1_old_coords[1]
                piece2.gridx = piece1_old_coords[2]
                piece2.gridy = piece1_old_coords[3]
                piece2.render()
                pieces_selected = []
                squares_selected = []
            if done:
                for square in self.board.squares:
                    square.selected = False
                return
            Button.listen()
            pygame.display.update()
            pygame.time.wait(10)

    def get_move(self, /, opnt):
        text_size = int(self.board.CONSTANT / 13)
        piece_slcted = ()
        name = self.name(text_size, with_comma=True)
        rect = name.get_rect()
        rect.centerx = self.board.x/2
        rect.centery = 30
        font = pygame.font.SysFont(DEFAULT_FONT, text_size)
        text = font.render("select a piece", True, Colors.BLACK)
        text2 = font.render("and move it.", True, Colors.BLACK)
        textrect = text.get_rect()
        textrect2 = text2.get_rect()
        textrect.centerx = self.board.x/2
        textrect2.centerx = self.board.x/2
        textrect.centery = 66
        textrect2.centery = 102

        def render():
            nonlocal piece_slcted
            piece_slcted = ()
            self.display.fill(Colors.WHITE)
            self.display.blit(name, rect)
            self.display.blit(text, textrect)
            self.display.blit(text2, textrect2)
            self.board.render()
            self.render_pieces()
            opnt.render_pieces(view=Gamepiece.BACK_VIEW)

        def process_mouseclick():
            if piece_slcted:
                for square in open_squares:
                    if square.hovered():
                        strike = False
                        if square.state == Square.STRIKE:
                            strike = True
                            text = font.render("STRIKE!", True, Colors.BLACK)
                            center_text(text, self.display, x=self.board.x / 2)
                        for open_square in open_squares:
                            open_square.render()
                        open_squares.remove(square)
                        coords = square.get_coords()[2:]
                        piece = piece_slcted[0]
                        move = ((piece.gridx, piece.gridy), coords)
                        self.last_two_moves = self.last_two_moves[1], move
                        piece.move(square, self, opnt)
                        if strike:
                            square.render(mode=Square.STRIKE)
                            pygame.display.update()
                            wait(1500)
                        return True
            return False
        render()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if warn_to_leave(self.display):
                            exit_game()
                        else:
                            render()
                    elif event.key == pygame.K_F1:
                        show_ranks(self.display, self)
                        render()
                    elif event.key == pygame.K_F2:
                        show_gamepiece_log(self.display, self, opnt)
                        render()
                elif event.type == pygame.MOUSEBUTTONUP:
                    if process_mouseclick():
                        return
                    for piece in self.active_pieces():
                        if piece.hovered():
                            if piece_slcted:
                                for square in open_squares:
                                    square.render()
                                    enemy_piece = opnt.pieceat(square)
                                    if enemy_piece:
                                        enemy_piece.render(
                                            view=Gamepiece.BACK_VIEW)
                            open_squares = piece.get_open_squares(self, opnt)
                            open_squares = [self.board.get_square(*coords)
                                            for coords in open_squares]
                            if open_squares:
                                pos = piece.get_pos()[2:]
                                piece_slcted = (piece,
                                                self.board.get_square(*pos))
                                for square in open_squares:
                                    coords = square.get_coords()[2:]
                                    if opnt.is_square_occupied(coords):
                                        square.render(Square.STRIKE)
                                    else:
                                        square.render(Square.ACTIVE)
                elif event.type == pygame.QUIT:
                    exit_game()
                elif event.type in EVENTS:
                    render()
            pygame.display.update()
            pygame.time.wait(10)

    def is_square_occupied(self, /, coords):
        if isinstance(coords, Square):
            coords = coords.get_coords()[2:]
        for piece in self.active_pieces():
            if piece.get_pos()[2:] == coords:
                return True
        return False

    def pieceat(self, /, coords):
        if isinstance(coords, Square):
            coords = coords.get_coords()[2:]
        for piece in self.active_pieces():
            if piece.get_pos()[2:] == coords:
                return piece
        return None

    def active_pieces(self, /):
        pieces = []
        for piece in self.pieces:
            if piece.state == Gamepiece.ACTIVE:
                pieces.append(piece)
        return pieces

    def has_movable_pieces(self, /, opnt):
        for piece in self.pieces:
            if piece.state == Gamepiece.ACTIVE:
                if piece.get_open_squares(self, opnt):
                    return True
        return False

    def name(self, /, font_size=20, with_comma=False):
        """
        Return a text object with the player's name written in his color, in
        the supplied font size.
        """
        try:
            font_size = int(font_size)
        except ValueError as e:
            raise ValueError("Player.get_name() expected int-like object, "
                             f"got {font_size!r}") from e
        font = pygame.font.SysFont(DEFAULT_FONT, font_size)
        if with_comma:
            text = self.playername + ','
        else:
            text = self.playername
        return font.render(text, True, self.color)
