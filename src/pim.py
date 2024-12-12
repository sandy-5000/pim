import sys
import os
import curses
from utils.pim_editor import pim_editor


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: pim <file-name>')
        sys.exit(1)

    file_name = sys.argv[1]

    if os.path.exists(file_name):
        if not os.path.isfile(file_name):
            print(f"The path '{file_name}' is not a file.")
            sys.exit(1)

    curses.wrapper(pim_editor, file_name)
