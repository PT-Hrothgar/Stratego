from stratego.buttons import Button, pygame
from stratego.colors import Colors
from stratego.gamepieces import Gamepiece
from stratego.features import show_gamepiece_log, show_ranks, warn_to_leave
from stratego.backend import (
    notify_about_click,
    exit_game,
    center_text,
    concat_surfaces,
    wait,
    GAMEPIECE_WIDTH,
    GAMEPIECE_HEIGHT,
    EVENTS,
    DEFAULT_FONT,
    FANCY_FONT
)
import sys


def game_intro(display):
    """Display the main game screen on the specified display."""
    if not isinstance(display, pygame.Surface):
        msg = f"game_intro() expected pygame.Surface object, got {display!r}"
        raise TypeError(msg)

    # Write "STRATEGO" in big Castellar letters
    castellar = pygame.font.SysFont(FANCY_FONT, 80)
    text = castellar.render("STRATEGO", True, Colors.BLACK)

    display_width = display.get_width()
    x1 = display_width/2 - 250
    x2 = display_width/2 + 150
    y = display.get_height() - 150
    def render():
        display.fill(Colors.WHITE)
        center_text(text, display, y=150)
        Button.clear_all_buttons()
        Button("Play", x1, y, 100, 50, Colors.DULL_GREEN, Colors.GREEN,
               display, notify_about_click, (True,))
        Button("Exit", x2, y, 100, 50, Colors.DULL_RED, Colors.RED, display,
               exit_game)

    render()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                if Button.process_click():
                    return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if warn_to_leave(display):
                        exit_game()
                    else:
                        render()
            elif event.type == pygame.QUIT:
                exit_game()
            elif event.type in EVENTS:
                render()
        Button.listen()
        pygame.display.update()
        pygame.time.wait(10)


def start_game(display, player1, player2):
    if not isinstance(display, pygame.Surface):
        msg = f"start_game() expected pygame.Surface object, got {display!r}"
        raise TypeError(msg)

    display_width = display.get_width()
    display_height = display.get_height()
    font = pygame.font.SysFont(DEFAULT_FONT, 30)
    text = font.render("and", True, Colors.BLACK)
    rect = text.get_rect()
    rect.centerx = display_width/2
    rect.top = 135

    name1 = player1.name(30)
    rect1 = name1.get_rect()
    rect1.right = display_width/2 - rect.width/2 - 12
    rect1.top = 135

    name2 = player2.name(30, with_comma=True)
    rect2 = name2.get_rect()
    rect2.left = display_width/2 + rect.width/2 + 12
    rect2.top = 135

    text2 = font.render("the game is about to begin!", True, Colors.BLACK)
    its_rect = text2.get_rect()
    its_rect.centerx = display_width/2
    its_rect.top = 171

    small_font = pygame.font.SysFont(DEFAULT_FONT, 15)
    shortcuts = [
        small_font.render("Keyboard Shortcuts:", True, Colors.BLACK),
        small_font.render("F1: Show Ranks", True, Colors.BLACK),
        small_font.render("F2: Show Gamepiece Log", True, Colors.BLACK),
        small_font.render("Escape: Close Game", True, Colors.BLACK)
    ]
    if sys.platform == "darwin":
        shortcuts.append(small_font.render("Command-H: Hide Game", True,
                                           Colors.BLACK))
    x1 = display_width/2 - 300
    x2 = display_width/2 + 150
    y = display_height - 150

    def render():
        y = display_height - 150
        display.fill(Colors.WHITE)
        Button.clear_all_buttons()
        Button("Let's Go!", x1, y, 150, 50, Colors.DULL_GREEN, Colors.GREEN,
               display, notify_about_click, (True,))
        Button("Exit", x2, y, 150, 50, Colors.DULL_RED, Colors.RED, display,
               exit_game)
        display.blit(text, rect)
        display.blit(name1, rect1)
        display.blit(name2, rect2)
        display.blit(text2, its_rect)
        for string in reversed(shortcuts):
            little_rect = string.get_rect()
            little_rect.center = (display_width/2, y)
            display.blit(string, little_rect)
            y -= 18

    render()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                if Button.process_click():
                    return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if warn_to_leave(display):
                        exit_game()
                    else:
                        render()
            elif event.type == pygame.QUIT:
                exit_game()
            elif event.type in EVENTS:
                render()
        Button.listen()
        pygame.display.update()
        pygame.time.wait(10)


def start_moves(display, mover):
    if not isinstance(display, pygame.Surface):
        msg = f"start_moves() expected pygame.Surface object, got {display!r}"
        raise TypeError(msg)

    name = mover.name(30, with_comma=True)
    done = False
    font = pygame.font.SysFont(DEFAULT_FONT, 30)
    text = font.render("make your first move!", True, Colors.BLACK)
    btn_x = display.get_width()/2 - 50
    btn_y = display.get_height() - 150
    def render():
        display.fill(Colors.WHITE)
        center_text(name, display, y=150)
        center_text(text, display, y=190)
        Button.clear_all_buttons()
        Button("Go!", btn_x, btn_y, 100, 50, Colors.DULL_GREEN, Colors.GREEN,
               display, notify_about_click, (True,))
    render()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                if Button.process_click():
                    done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if warn_to_leave(display):
                        exit_game()
                    else:
                        render()
                elif event.key == pygame.K_RETURN:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                    done = True
            elif event.type == pygame.QUIT:
                exit_game()
            elif event.type in EVENTS:
                render()
        if done:
            return
        Button.listen()
        pygame.display.update()
        pygame.time.wait(10)


def show_move(display, moving_player, other):
    if not isinstance(display, pygame.Surface):
        msg = f"show_move() expected pygame.Surface object, got {display!r}"
        raise TypeError(msg)

    font_size = int(moving_player.board.CONSTANT / 13)
    font = pygame.font.SysFont(DEFAULT_FONT, font_size)
    x = moving_player.board.x / 2
    display_height = display.get_height()
    y = display_height / 2
    move = moving_player.last_two_moves[1]
    start_square = moving_player.board.get_square(*move[0])
    end_square = moving_player.board.get_square(*move[1])
    mover = moving_player.pieceat(move[1])
    mover.x_pos, mover.y_pos = start_square.x, start_square.y
    mover.gridx, mover.gridy = start_square.gridx, start_square.gridy

    def render(mode=0):
        display.fill(Colors.WHITE)
        moving_player.board.render()
        moving_player.render_pieces(view=Gamepiece.BACK_VIEW)
        other.render_pieces(view=Gamepiece.BACK_VIEW)
        if mode != None:
            if mode == 0:
                text = "Show Move"
            elif mode == 1:
                display.blit(name, rect)
                text = "Make Next Move"
            elif mode > 1:
                if mode == 2:
                    flag.render(view=Gamepiece.LIGHTENED)
                elif mode == 3:
                    display.blit(name, namerect)
                    display.blit(msg, rect)
                    other.render_pieces()
                text = "Continue"
            btn_x = 8
            width = moving_player.board.CONSTANT - 16
            Button.clear_all_buttons()
            Button(text, btn_x, y-25, width, 40, Colors.DULL_GREEN,
                   Colors.GREEN, display, notify_about_click, (True,))
    def game_loop(mode=0):
        done = False
        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP:
                    if Button.process_click():
                        done = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if warn_to_leave(display):
                            exit_game()
                        else:
                            render(mode=mode)
                    elif event.key == pygame.K_RETURN:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                        done = True
                elif event.type == pygame.QUIT:
                    exit_game()
                elif event.type in EVENTS:
                    render(mode=mode)
            if done:
                break
            Button.listen()
            pygame.display.update()
            pygame.time.wait(10)
    render()
    game_loop()

    Button.clear_all_buttons()
    render(mode=None)
    strike = False
    if other.is_square_occupied(end_square):
        text = font.render("STRIKE!", True, Colors.BLACK)
        center_text(text, display, x=x)
        attacked = other.pieceat(end_square)
        strike = True
    mover.move(end_square, moving_player, other, backside=True)
    if strike:
        # Overwrite the word "Strike"
        pygame.draw.rect(display, Colors.WHITE,
                         (0, 0, moving_player.board.x, display_height))
        vs = font.render("vs.", True, Colors.BLACK)
        dies = font.render(" dies!", True, Colors.BLACK)
        center_text(vs, display, x=x)

        mover.render()
        name1 = mover.get_name(font_size)
        rect1 = name1.get_rect()
        rect1.centery = y - font_size - 6
        rect1.centerx = x
        display.blit(name1, rect1)
        pygame.display.update()
        wait(1500)

        attacked.render()
        name2 = attacked.get_name(font_size)
        rect2 = name2.get_rect()
        rect2.centery = y + font_size + 6
        rect2.centerx = x
        display.blit(name2, rect2)
        text = font.render("The victor is:", True, Colors.BLACK)
        rect = text.get_rect()
        rect.centery = y + font_size*2 + 12
        rect.centerx = x
        display.blit(text, rect)
        pygame.display.update()
        wait(1500)

        result = test_strike(mover.rank, attacked.rank)
        if result is None:
            text = font.render("Neither one!", True, Colors.BLACK)
            losers = [mover, attacked]

        elif result == False:
            rect2.centery = y + font_size * 3 + 18
            display.blit(name2, rect2)
            text = concat_surfaces(name1, dies)
            losers = [mover]

        else:
            rect1.centery = y + font_size * 3 + 18
            display.blit(name1, rect1)
            text = concat_surfaces(name2, dies)
            losers = [attacked]

        rect = text.get_rect()
        if losers[1:]:
            rect.centery = y + font_size * 3 + 18
        else:
            rect.centery = y + font_size * 4 + 24
        rect.centerx = x
        display.blit(text, rect)

        for loser in losers:
            loser.render(view=Gamepiece.LIGHTENED)
            pygame.display.update()
            wait(1500)
            if loser.rank == "Flag":
                flag = loser
                render(mode=2)
                game_loop(mode=2)
                return True
            loser.die()

    def get_rect(text):
        rect = text.get_rect()
        rect.center = (x, y-45)
        return rect

    if other.has_movable_pieces(moving_player):
        name = other.name(font_size, with_comma=True)
        rect = get_rect(name)
        render(mode=1)
        game_loop(mode=1)
        return False

    else:
        name = other.name(font_size)
        namerect = name.get_rect()
        namerect.center = (x, y-81)
        msg = font.render("has no legal moves!", True, Colors.BLACK)
        rect = get_rect(msg)
        render(mode=3)
        game_loop(mode=3)
        return True


def test_strike(rank1, rank2):
    if rank1 == rank2:
        return None
    if isinstance(rank1, int) and isinstance(rank2, int):
        return rank1 < rank2
    # Note that since rank1 is the moving piece, it cannot be a bomb or
    # a flag.
    if rank2 == "Bomb":
        return rank1 == 8
    elif rank2 == "Flag":
        return "Flag"
    elif rank2 == "Spy":
        return True
    if rank1 == "Spy":
        return rank2 == 1


def show_win(display, player1, player2):
    if player1.victorious:
        victor, loser = player1, player2
    else:
        victor, loser = player2, player1
    font = pygame.font.SysFont(DEFAULT_FONT, 30)
    text = font.render("has won!", True, Colors.BLACK)
    name = victor.name(30)
    flag_img = loser.pieces[-1].img
    x = display.get_width()/2 - GAMEPIECE_WIDTH/2
    y = display.get_height()/2 - GAMEPIECE_HEIGHT/2
    rectangle = pygame.Surface((GAMEPIECE_WIDTH*2 + 80, 15), pygame.SRCALPHA)
    rectangle.fill(victor.color)
    rectangle = pygame.transform.rotate(rectangle, 45)
    rect = rectangle.get_rect(center=display.get_rect().center)
    btn_x = display.get_width()/2 - 50
    btn_y = display.get_height() - 150

    def render():
        display.fill(Colors.WHITE)
        center_text(name, display, y=50)
        center_text(text, display, y=86)
        display.blit(flag_img, (x, y))
        display.blit(rectangle, rect)
        Button.clear_all_buttons()
        Button("Home", btn_x, btn_y, 100, 50, Colors.DARK_BLUE, Colors.BLUE,
               display, notify_about_click, (True,))
    render()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                if Button.process_click():
                    return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if warn_to_leave(display):
                        exit_game()
                    else:
                        render()
                elif event.key == pygame.K_RETURN:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                    return
            elif event.type == pygame.QUIT:
                exit_game()
            elif event.type in EVENTS:
                render()
        Button.listen()
        pygame.display.update()
        pygame.time.wait(10)
