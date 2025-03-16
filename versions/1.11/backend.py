# Note that it will be very inefficient for every ``stratego`` module
# that uses it to import ``pygame`` separately, as it is so large.
# So, it will only be actually imported from here, ``stratego.backend``,
# and then any other module that uses it can import it from here.
import pygame
import datetime
import os
import sys
pygame.init()

SESSION_ID = str(int(len(os.listdir('.')) / 24))
GAMEPIECE_WIDTH = 50
GAMEPIECE_HEIGHT = 70
EVENTS = (pygame.WINDOWENTER, pygame.WINDOWEXPOSED, pygame.WINDOWFOCUSGAINED,
          pygame.WINDOWRESTORED, pygame.WINDOWSHOWN, pygame.WINDOWTAKEFOCUS)

if sys.platform == "darwin":
    DEFAULT_FONT = "menlo"
    FANCY_FONT = "academyengravedletfonts"
else:
    DEFAULT_FONT = "consolas"
    FANCY_FONT = "castellar"
if FANCY_FONT not in pygame.font.get_fonts():
    import warnings
    warnings.warn("{} font not available; defaulting to {}"
                  .format(FANCY_FONT, DEFAULT_FONT), stacklevel=1)
    FANCY_FONT = DEFAULT_FONT
print("Default font in use: {} - Fancy font in use: {}"
      .format(DEFAULT_FONT, FANCY_FONT))

def notify_about_click(param=None):
    """
    Simply return the passed parameter; this function can be used by
    buttons with separate parameters so that calling code can tell which
    button is being clicked.
    """
    return param


def center_text(text_obj, surface, *, x=None, y=None):
    if not x:
        x = int(surface.get_width() / 2)
    if not y:
        y = int(surface.get_height() / 2)

    rect = text_obj.get_rect()
    rect.center = (x, y)
    surface.blit(text_obj, rect)


def concat_surfaces(surface1, surface2, /):
    height1 = surface1.get_height()
    height2 = surface2.get_height()
    width1 = surface1.get_width()
    width2 = surface2.get_width()
    if height1 != height2:
        raise ValueError("concat_surfaces() expected two surfaces of the same"
                         "height.")
    newsurf = pygame.Surface((width1 + width2, height1), pygame.SRCALPHA)
    newsurf.blit(surface1, (0,0))
    newsurf.blit(surface2, (width1, 0))
    return newsurf


def wait(milliseconds, /):
    milliseconds = int(milliseconds)
    timedelta = datetime.timedelta(milliseconds=milliseconds)
    start_time = datetime.datetime.now()

    while True:
        pygame.event.get()
        if datetime.datetime.now() - start_time >= timedelta:
            return
        pygame.time.wait(1)


def exit_game():
    # We need to get rid of any files we may have created!
    for filename in os.listdir('.'):
        if filename.startswith(f"{SESSION_ID}-"):
            os.remove(filename)
    # Now exit:
    pygame.quit()
    raise SystemExit(0)
