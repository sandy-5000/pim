import sys
import curses
from .editor_state import EditorState
from .file_handler import open_file, save_file
from .key_handler import handle_backspace, handle_enter, handle_all_keys, handle_delete


def normal_mode(key, state):

    if state.command == '' and key == ord('i'):
        state.mode = 'INSERT'
    elif state.command == '' and key == ord('p'):
        state.paste_from_clipboard()
    elif state.command == '' and key == ord('B'):
        state.set_cursor_y(0 - state.view_y)
        state.set_cursor_x(0 - state.view_x)
    elif state.command == '' and key == ord('G'):
        state.set_cursor_y(len(state.text) - state.view_y)
        state.set_cursor_x(len(state.text[-1]) - state.view_x)
    elif key in (curses.KEY_BACKSPACE, 8, 127):
        if state.command:
            state.command = state.command[0:len(state.command) - 1]
    elif key in (curses.KEY_ENTER, 10, 13):
        state.command = state.command.strip()
        if state.command == ':q':
            return False
        elif state.command == ':w':
            save_file(state.file_name, state.text)
        elif state.command == ':r':
            open_file(state.file_name)
        elif state.command.startswith(':set '):
            r = state.command[5:]
            if r == 'nu':
                state.show_line_numbers = True
        elif state.command.startswith(':unset '):
            r = state.command[7:]
            if r == 'nu':
                state.show_line_numbers = False
        elif state.command.startswith(':y'):
            r = state.command[2:].split(',')
            if len(r) != 2:
                state.message = 'Invalid positions'
            else:
                state.copy_to_clipboard(r[0].strip(), r[1].strip())
        elif state.command.startswith(':d'):
            r = state.command[2:].split(',')
            if len(r) != 2:
                state.message = 'Invalid positions'
            else:
                state.cut_to_clipboard(r[0].strip(), r[1].strip())
        elif state.command.startswith(':'):
            r = state.command[1:].strip()
            try:
                line_number = int(r) - 1
                state.set_cursor_y(line_number - state.view_y)
                state.set_cursor_x(0 - state.view_x)
            except:
                state.message = 'Invalid command'
        else:
            state.message = 'Invalid command'
        state.command = ''
    elif key == ord(':'):
        state.command = ':'
    elif state.command and state.command[0] == ':':
        state.command = state.command + chr(key)
    return True


def handle_ctrl_operations(key, state):
    if key == 3:
        state.copy_selected()
    elif key == 22:
        state.paste_from_clipboard()
    elif key == 24:
        state.cut_selected()


def pim_editor(stdscr, file_name):
    curses.curs_set(1)
    curses.raw()

    text, error = open_file(file_name)
    if error != None:
        print('Error: coundn\'t read File: {file_name}')
        sys.exit(1)

    state = EditorState(stdscr)
    state.mode = 'NORMAL'
    state.text = text
    state.number_bar_width = len(str(len(text))) + 1
    state.view_y = 0
    state.set_cursor_x(0)
    state.set_cursor_y(0)
    state.file_name = file_name

    while True:

        state.refresh()
        key = stdscr.getch()
        if key in (curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT):
            state.move_cursor(key)
            continue
        if key in (547, 400, 548, 391):
            state.move_select_cursor(key)
            continue
        if key == 3:
            handle_ctrl_operations(key, state)
            stdscr.refresh()
            continue
        if state.mode == 'NORMAL':
            if not normal_mode(key, state):
                break
        elif state.mode == 'INSERT':
            if key == 27: # Esc
                state.mode = 'NORMAL'
                continue
            elif key == 330: # Delete
                handle_delete(state)
            elif key in (curses.KEY_BACKSPACE, 8, 127):  # Backspace
                handle_backspace(state)
            elif key in (curses.KEY_ENTER, 10, 13):  # Enter
                handle_enter(state)
            elif key in (22, 24):
                handle_ctrl_operations(key, state)
            else:
                handle_all_keys(state, key)
