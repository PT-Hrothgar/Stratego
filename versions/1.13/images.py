from PIL import Image as _Image
from PIL import ImageEnhance as _ImageEnhance
from PIL import ImageOps as _ImageOps
import os

from stratego.colors import Colors, pygame
from stratego.backend import SESSION_ID

LIGHTENING_FACTOR = 0.3
GAMEPIECE_WIDTH = 50
GAMEPIECE_HEIGHT = 70


def lighten_image(filename: str, /) -> pygame.surface.Surface:
    """
    Reduce the saturation of the image at a given filename.

    Parameter
    ---------
    filename: str, positional-only

    This function opens the image at the given filename and uses ``PIL`` to
    reduce the saturation of the colors in the image. Then it creates a
    temporary file with the reduced-color image and opens the file with
    ``pygame`` to create a ``pygame.Surface`` object. The temporary file is
    then deleted, and the ``pygame.Surface`` object containing the
    reduced-color image is returned.
    """
    if not isinstance(filename, str):
        raise ValueError(f"lighten_image() expected string, got {filename!r}")

    # Use PIL to reduce the saturation of the image to a new filename.
    img = _Image.open(filename)
    converter = _ImageEnhance.Color(img)
    new_img = converter.enhance(LIGHTENING_FACTOR)
    # Get the original filename without the .jpg extension.
    orig_filename = filename.split('.')[0]
    # Save the lightened image to the old filename plus "light".
    new_filename = f"{orig_filename}light.jpg"
    new_img.save(new_filename)
    # Delete all variables involved in the switch.
    del img, converter, new_img, orig_filename

    # Open the new image file.
    pygame_img = pygame.image.load(new_filename)

    # Delete the temporary image file.
    # Note that we will still be able to use the image itself through
    # the "pygame_img" object.
    os.remove(new_filename)

    # Return the faded image stored in "pygame_img"
    return pygame_img


def get_gamepiece_imgs(color: tuple, id, /) -> list:
    """
    Get the images of the Stratego gamepieces in the given color.

    Parameter
    ---------
    color: tuple, positional-only
    Must be either ``stratego.colors.Colors.RED`` or
    ``stratego.colors.Colors.BLUE``

    The function opens the file containing the images of the gamepieces in the
    given color, and then, from the opened file, creates a list containing the
    image for each individual gamepiece in the given color in the form of a
    ``pygame.Surface`` object. This list is
    then returned.
    """

    match color:
        case Colors.PLAYER_RED:
            image = _Image.open("redpieces.jpg")
            return parse_image(image, id)
        case Colors.PLAYER_BLUE:
            image = _Image.open("bluepieces.jpg")
            return parse_image(image, id)
        case _:
            raise ValueError("get_gamepiece_imgs() expected either "
                             "``stratego.colors.Colors.RED`` or ``stratego."
                             f"colors.Colors.BLUE``, got {color!r}")


def parse_image(image, id, /) -> list:
    """
    Return the list of the dozen different gamepieces contained in the
    image, in the order Marshall, General, Colonel, Major, Captain,
    Lieutenant, Sergeant, Miner, Scout, Spy, Bomb, Flag, all in the form of
    ``pygame.Surface`` objects.
    """
    piece_list = []
    counter = 0
    # The gamepieces are arranged (in the image) in a 4x3 grid.
    # Each piece is 50 pixels by 70 pixels (these
    # numbers are stored in the ``stratego.backend`` module in
    # ``GAMEPIECE_WIDTH`` and ``GAMEPIECE_HEIGHT``). So, the entire
    # image is 200 by 210 pixels.
    #
    # We will go through the image one row at a time - taking each row
    # one piece at a time.
    for x_coord in range(0, GAMEPIECE_WIDTH * 4, GAMEPIECE_WIDTH):
        for y_coord in range(0, GAMEPIECE_HEIGHT * 3, GAMEPIECE_HEIGHT):
            right_x_coord = x_coord + GAMEPIECE_WIDTH
            bottom_y_coord = y_coord + GAMEPIECE_HEIGHT
            filename = f"{SESSION_ID}-gamepiece{id}{counter}.jpg"
            # Crop the gamepiece at the given coordinates from the image
            new = image.crop((x_coord, y_coord, right_x_coord, bottom_y_coord))
            new.save(filename)
            piece_list.append(filename)
            counter += 1

    return piece_list


def flip_img(filename: str, /):
    """
    Return a pygame.Surface containing the image at the given filename
    flipped horizontally.
    """
    new_filename = f"{filename}_flipped.jpg"
    img = _Image.open(filename)
    new_img = _ImageOps.mirror(img)
    new_img.save(new_filename)
    new_img_as_surface = pygame.image.load(new_filename)
    os.remove(new_filename)
    return new_img_as_surface
