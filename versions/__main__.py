"""stratego - Play the board game Stratego with two players"""
print("Initializing stratego...")
import os
images_dir = __file__.replace("__main__.py", "images")
os.chdir(images_dir)
del images_dir

from stratego.players import Player, pygame
from stratego.boards import Board
from stratego.backend import exit_game
from stratego.game_loops import (
    game_intro,
    start_game,
    start_moves,
    show_move,
    show_win,
)


def main():
    # Create the game window
    display = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
    print("Created display with width: {} and height: {}"
          .format(display.get_width(), display.get_height()))
    pygame.scrap.init()

    try:
        # Set up an infinite loop to play as many games as necessary.
        while True:
            Player.reset()
            pygame.display.set_caption("Stratego")
            board = Board(display)
            print(f"Total game board width and height: {board.totalsize}")
            player1 = Player(display, board)
            player2 = Player(display, board)

            # Display the main game screen with "Play" and "Exit".
            game_intro(display)
            # If game_intro() did not exit, the user must have clicked "Play".
            # Get the names of the two players.
            player1.get_name()
            player2.get_name(forbidden_name=player1.playername)
            if player1.color == Player.PLAYER_RED:
                start_player = player1
                second_player = player2
            else:
                start_player = player2
                second_player = player1

            pygame.display.set_caption("Stratego - {} vs. {}".format(
                start_player.playername, second_player.playername))
            # Inform the players that the game is about to start.
            # (They can still exit at this point.)
            start_game(display, start_player, second_player)
            # Let the players set up their pieces.
            start_player.setup()
            second_player.setup()

            # Start the game using start_moves().
            start_moves(display, start_player)

            # All these functions can exit the program nicely on their own
            # if the user closes the window or presses "Esc".
            # Thus, we do not need to worry about game-exiting logic here,
            # and just set up an infinite loop.
            while True:
                start_player.get_move(second_player)
                if show_move(display, start_player, second_player):
                    start_player.victorious = True
                    break

                second_player.get_move(start_player)
                if show_move(display, second_player, start_player):
                    second_player.victorious = True
                    break

            # One player must have won.
            show_win(display, player1, player2)

    except BaseException as msg:
        print(f"Exited game with error message: {msg!r}")
        exit_game()


if __name__ == "__main__":
    main()
