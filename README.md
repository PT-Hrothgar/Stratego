# Stratego

This is the source code for my Stratego Python program. It is a simulation of the board game [Stratego](https://en.wikipedia.org/wiki/Stratego) for two players to play in pass-and-play style.

I don't think versions 1.10 and earlier exist anywhere, but versions 1.11-1.13 are available here. Version 2.0 is in development, and I will upload it here when it is complete.

## Requirements

Python version 1.10 or later\
`pygame` module\
`PIL` module

### Some random code

```python
import sys

alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"

mode_val = 0
if sys.argv[1:]:
    mode_val = int(sys.argv[1])
assert mode_val in (0, 1)
# 0 for Encode (default), 1 for Decode
MODE = "Decoding" if mode_val else "Encoding"


def move_by_one(x):
    y = x + 2*mode_val - 1
    return y % 5


def process_str(x):
    x = x.replace(" ", "").upper().replace("J", "I")
    if x:
        assert x.isalpha()
    return x


def get_coords(x):
    for a in range(5):
        try:
            b = grid[a].index(x)
        except ValueError:
            return None
        else:
            return a, b


def code(msg):
    if msg[2:]:
        return "".join((code(msg[:2]), code(msg[2:])))
    elif msg[1:]:
        a, b = msg
        if a == b:
            return msg

        x1, y1 = get_coords(a)
        x2, y2 = get_coords(b)
        if x1 == x2:
            x3 = x4 = x1
            y3, y4 = move_by_one(y1), move_by_one(y2)
        elif y1 == y2:
            x3, x4 = move_by_one(x1), move_by_one(x2)
            y3 = y4 = y1
        else:
            x3, x4 = x1, x2
            y3, y4 = y2, y1
        c = grid[x3][y3]
        d = grid[x4][y4]
        return "".join((c, d))
    else:
        return msg


if __name__ == "__main__":
    print("""
{} Playfair Code
----------------------""".format(MODE))

    kwd = input("Enter a keyword: ")
    msg = input("Enter a message (default 'Hello World'): ")
    kwd = process_str(kwd)
    msg = process_str(msg)
    if not msg:
        msg = "HELLOWORLD"
    print("{} message '{}' with keyword '{}'".format(MODE, msg, kwd))

    letters = "".join((kwd, alphabet))
    grid = [[]]
    while letters:
        if grid[-1][4:]:
            grid.append([])
        char = letters[0]
        grid[-1].append(char)
        letters = letters.replace(char, "")

    result = code(msg)
    print("Result is: '{}'".format(result))
```
