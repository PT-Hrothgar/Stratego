from stratego.buttons import Button, pygame
from stratego.colors import Colors
from stratego.backend import (
    notify_about_click,
    exit_game,
    center_text,
    GAMEPIECE_WIDTH,
    GAMEPIECE_HEIGHT,
    EVENTS,
    DEFAULT_FONT
)


def show_gamepiece_log(display, player1, player2):
    font_size = int(player1.board.CONSTANT / 13)
    x = player1.board.x / 2
    font = pygame.font.SysFont(DEFAULT_FONT, font_size)
    text = (
        font.render("Gamepiece Log", True, Colors.BLACK),
        font.render("Faded pieces are", True, Colors.BLACK),
        font.render("dead.", True, Colors.BLACK)
    )
    def render():
        display.fill(Colors.WHITE)
        y = font_size
        for string in text:
            rect = string.get_rect()
            rect.center = (x, y)
            display.blit(string, rect)
            y += font_size + 6
        player1.board.render()
        for piece in player1.pieces:
            piece.show_orig_pos()
        for piece in player2.pieces:
            piece.show_orig_pos()
        Button.clear_all_buttons()
        Button("Leave", x-50, display.get_height()/2, 100, 50,
               Colors.DULL_GREEN, Colors.GREEN, display, notify_about_click,
               (True,))
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


def show_ranks(display, player):
    surface = pygame.Surface((GAMEPIECE_WIDTH * 12 + 35 * 11,
                              GAMEPIECE_HEIGHT + 65))
    surface.fill(Colors.WHITE)
    x = 0
    width = display.get_width()
    height = display.get_height()

    bigfont = pygame.font.SysFont(DEFAULT_FONT, 30)
    text = bigfont.render("Ranks", True, Colors.BLACK)
    font = pygame.font.SysFont(DEFAULT_FONT, 12)
    for piece in player.pieces:
        if piece.representative:
            surface.blit(piece.img, (x, 0))
            name = font.render(piece.name, True, Colors.BLACK)
            surface.blit(name, (x, GAMEPIECE_HEIGHT + 5))
            if isinstance(piece.rank, int):
                number = font.render(str(piece.rank), True, Colors.BLACK)
                surface.blit(number, (x, GAMEPIECE_HEIGHT + 25))
            num = font.render(f"({piece.representative}x)", True, Colors.BLACK)
            surface.blit(num, (x, GAMEPIECE_HEIGHT + 45))
            x += GAMEPIECE_WIDTH + 35

    def render():
        display.fill(Colors.WHITE)
        center_text(text, display, y=50)
        Button.clear_all_buttons()
        Button("Leave", width/2-50, height-75, 100, 50, Colors.DULL_GREEN,
               Colors.GREEN, display, notify_about_click, (True,))
        # Spoiler: center_text() can center anything, not just text
        center_text(surface, display)
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


def warn_to_leave(display, /):
    blacksurf = pygame.Surface((600, 800))
    blacksurf.fill(Colors.BLACK)
    whitesurf = pygame.Surface((596, 796))
    whitesurf.fill(Colors.WHITE)
    font = pygame.font.SysFont(DEFAULT_FONT, 30)
    text = font.render("Do you want to close game?", True, Colors.BLACK)
    center_text(whitesurf, blacksurf)
    center_text(text, blacksurf, y=250)
    center_text(blacksurf, display)
    x = display.get_width()/2 - 100
    y1 = display.get_height()/2  - 100
    y2 = display.get_height()/2
    Button.clear_all_buttons()
    Button("Yes [Y]", x, y1, 200, 50, Colors.DULL_RED, Colors.RED, display,
           notify_about_click, (True,))
    Button("No [N]", x, y2, 200, 50, Colors.DULL_GREEN, Colors.GREEN, display,
           notify_about_click, (False,))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                result = Button.process_click()
                if result == True:
                    return True
                elif result == False:
                    return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                    return True
                elif event.key == pygame.K_n:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                    return False
            elif event.type == pygame.QUIT:
                exit_game()

        Button.listen()
        pygame.display.update()
        pygame.time.wait(10)
