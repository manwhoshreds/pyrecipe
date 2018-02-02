from curses import wrapper
from pyrecipe.recipe import Recipe

def main(stdscr):
    # Clear screen
    stdscr.clear()
    r = Recipe('pesto') 

    stdscr.addstr(str(r))

    stdscr.refresh()
    stdscr.getkey()
    

wrapper(main)
