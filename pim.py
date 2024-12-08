import sys
import os
import curses
import pyperclip


file_name = None

mode = 'NORMAL'
command = ''
message = ''
text = ['']
view_y = 0
cursor_x = 0
cursor_y = 0
height, width = 0, 0
view_port = ['']
view_port_height = 0
number_set = True

number_bar_width = 2


def open_file():
    global text
    global file_name

    try:
        with open(file_name) as f:
            text = f.read().splitlines()
    except PermissionError:
        print(f"Permission denied to open the file: {file_name}")
    except Exception:
        text = ['']


def save_file():
    global text
    global file_name

    with open(file_name, 'w') as f:
        for line in text:
            f.write(line + '\n')


def arrow_keys(key):
    global text
    global view_y
    global cursor_x
    global cursor_y
    global width
    global height
    global view_port
    global view_port_height

    if key == curses.KEY_LEFT and cursor_x == 0 and cursor_y == 0:
        return
    if key == curses.KEY_RIGHT and cursor_x == len(view_port[-1]) \
        and cursor_y == len(view_port) - 1:
        return

    match key:
        case curses.KEY_UP:
            cursor_y = max(0, cursor_y - 1)
            if cursor_y == 0:
                view_y = max(0, view_y - 1)
        case curses.KEY_DOWN:
            cursor_y = min(view_port_height - 1, cursor_y + 1)
            if cursor_y == view_port_height - 1:
                view_y = min(len(text) - 1, view_y + 1)
        case curses.KEY_LEFT:
            if cursor_x == 0:
                cursor_y = max(0, cursor_y - 1)
                if cursor_y == 0:
                    view_y = max(0, view_y - 1)
                cursor_x = width
            else:
                cursor_x = cursor_x - 1
        case curses.KEY_RIGHT:
            if cursor_x == len(text[view_y + cursor_y]):
                cursor_y = min(view_port_height - 1, cursor_y + 1)
                if cursor_y == view_port_height - 1:
                    view_y = min(len(text) - 1, view_y + 1)
                cursor_x = 0
            else:
                cursor_x = cursor_x + 1
    cursor_y = min(cursor_y, len(view_port) - 1)
    try:
        cursor_x = min(len(text[view_y + cursor_y]), cursor_x)
    except:
        cursor_x = 0


def handle_backspace():
    global text
    global view_y
    global cursor_x
    global cursor_y
    global number_bar_width

    index_y = cursor_y + view_y
    if cursor_x > 0:
        text[index_y] = text[index_y][:cursor_x - 1] + text[index_y][cursor_x:]
        cursor_x -= 1
    elif index_y > 0:
        prev_line_len = len(text[index_y - 1])
        text[index_y - 1] += text[index_y]
        text.pop(index_y)
        if cursor_y == 0:
            view_y = max(0, view_y - 1)
        else:
            cursor_y -= 1
        cursor_x = prev_line_len
    number_bar_width = len(str(len(text))) + 1


def handle_enter():
    global text
    global view_y
    global cursor_x
    global cursor_y
    global view_port_height
    global number_bar_width

    index_y = cursor_y + view_y
    new_line = text[index_y][cursor_x:]
    text[index_y] = text[index_y][:cursor_x]
    s = text[index_y]
    spaces_len = len(s) - len(s.lstrip(' '))
    spaces = ' ' * spaces_len
    text.insert(index_y + 1, spaces + new_line)
    if cursor_y + 1 >= view_port_height - 1:
        view_y += 1
    if cursor_y < view_port_height - 1:
        cursor_y += 1
    cursor_x = spaces_len
    number_bar_width = len(str(len(text))) + 1


def paste_from_clipboard():
    global text
    global width
    global view_y
    global cursor_x
    global cursor_y
    global view_port_height
    global number_bar_width

    copied_text = pyperclip.paste()
    copied_text = copied_text.replace('\r', '').replace('\t', ' ' * 4)
    index_y = cursor_y + view_y
    new_line = text[index_y][:cursor_x] + copied_text + text[index_y][cursor_x:]
    btw_lines = [*new_line.split('\n')]
    text = text[:index_y] + btw_lines + text[index_y + 1:]
    length = len(btw_lines) - 1
    if cursor_y + length >= view_port_height - 1:
        view_y += cursor_y + length - view_port_height + 1
    cursor_y = min(view_port_height - 1, cursor_y + length)
    if length:
        cursor_x = len(btw_lines[-1])
    else:
        cursor_x = min(cursor_x + len(copied_text), width)
    number_bar_width = len(str(len(text))) + 1


def copy_to_clipboard(start, end):
    global text
    global view_y
    global cursor_x
    global cursor_y
    global message

    if start != '' and start != '.':
        try:
            start = int(start)
        except:
            message = 'Invalid number format'
            return
    if end != '' and end != '.':
        try:
            end = int(end)
        except:
            message = 'Invalid number format'
            return

    start_x, start_y = 0, 0
    end_x = len(text[-1]) - 1 if text else 0
    end_y = len(text) - 1

    if start == '.':
        start_x = cursor_x
        start_y = view_y + cursor_y
    elif start != '':
        start_y = max(0, start - 1)
        start_x = 0

    if end == '.':
        end_x = cursor_x - 1
        end_y = view_y + cursor_y
    else:
        end_y = min(end - 1, len(text) - 1)
        end_x = len(text[end_y]) - 1

    if [start_y, start_x] > [end_y, end_x]:
        message = 'Invalid Range'
        return

    text_to_copy = ''
    if start_y == end_y:
        text_to_copy = text[start_y][start_x:end_x + 1]
    else:
        for y in range(start_y, end_y + 1):
            if y == end_y:
                text_to_copy += text[y][:end_x + 1] + '\n'
            elif y == start_y:
                text_to_copy += text[y][start_x:] + '\n'
            else:
                text_to_copy += text[y] + '\n'
    pyperclip.copy(text_to_copy)
    message = f'yanked {end_y - start_y + 1} lines.'


def handle_all_keys(key):
    global text
    global view_y
    global cursor_x
    global cursor_y

    char = chr(key)
    if char == '\t':
        char = '    '
    index_y = cursor_y + view_y
    text[index_y] = text[index_y][:cursor_x] + char + text[index_y][cursor_x:]
    cursor_x += len(char)


def normal_mode(key):
    global mode
    global command
    global number_set
    global message

    if command == '' and key == ord('i'):
        mode = 'INSERT'
    elif command == '' and key == ord('p'):
        paste_from_clipboard()
    elif key in (curses.KEY_BACKSPACE, 127, 8):
        if command:
            command = command[0:len(command) - 1]
    elif key in (curses.KEY_ENTER, 10):
        command = command.strip()
        if command == ':q':
            return False
        elif command == ':w':
            save_file()
        elif command == ':r':
            open_file()
        elif command.startswith(':set'):
            r = command[4:]
            if r == 'nu':
                number_set = True
        elif command.startswith(':unset'):
            r = command[6:]
            if r == 'nu':
                number_set = False
        elif command.startswith(':y'):
            r = command[2:].split(',')
            if len(r) != 2:
                message = 'Invalid positions'
            else:
                copy_to_clipboard(r[0].strip(), r[1].strip())
        else:
            message = 'Invalid command'
        command = ''
    elif key == ord(':'):
        command = ':'
    elif command and command[0] == ':':
        command = command + chr(key)
    return True


def draw_screen(stdscr):
    global mode
    global command
    global text
    global view_y
    global cursor_x
    global cursor_y
    global height
    global width
    global view_port
    global view_port_height
    global number_bar_width
    global number_set
    global message

    height, width = stdscr.getmaxyx()
    view_port_height = height - 2

    stdscr.clear()

    view_port = text[view_y:view_y + view_port_height]
    for idx, line in enumerate(view_port):
        line_number = idx + view_y + 1
        trimmed_line = line[:width - number_bar_width]
        line_number = str(line_number).rjust(number_bar_width - 1) + ' '
        if not number_set:
            line_number = ''
        line_to_display = f'{line_number}{trimmed_line}'
        stdscr.addstr(idx, 0, line_to_display)

    command_width = width - 20
    mode_or_cmd = f'-- {mode} --'
    if mode == 'NORMAL' and command:
        mode_or_cmd = command
        message = ''
    if mode == 'NORMAL' and message:
        mode_or_cmd = message
    width_diff = command_width - len(mode_or_cmd)
    if width_diff > 0:
        mode_or_cmd += ' ' * width_diff
    elif width_diff < 0:
        mode_or_cmd = mode_or_cmd[-command_width:]
    stdscr.addstr(height - 2, 0, f"File: {file_name[:width - 6]}")
    stdscr.addstr(height - 1, 0, f"{mode_or_cmd} Line: {cursor_y + view_y + 1}, Col: {cursor_x + 1}")
    line_number_padding = number_bar_width if number_set else 0
    stdscr.move(cursor_y, line_number_padding + cursor_x)
    stdscr.refresh()


def main(stdscr):
    global mode
    global text
    global view_y
    global cursor_x
    global cursor_y
    global height
    global width
    global view_port
    global number_bar_width

    curses.curs_set(1)

    mode = "NORMAL"
    open_file()
    number_bar_width = len(str(len(text))) + 1
    view_y = 0
    cursor_x = 0
    cursor_y = 0

    while True:

        draw_screen(stdscr)
        key = stdscr.getch()

        if key in (curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT):

            arrow_keys(key)
            continue

        if mode == "NORMAL":
            if not normal_mode(key):
                break
        elif mode == "INSERT":
            if key == 27: # Esc
                mode = "NORMAL"
                continue
            elif key in (curses.KEY_BACKSPACE, 127, 8):  # Backspace
                handle_backspace()
            elif key in (curses.KEY_ENTER, 10):  # Enter
                handle_enter()
            else:
                handle_all_keys(key)



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python pim.py <file-name>')
        sys.exit(1)

    file_name = sys.argv[1]

    if os.path.exists(file_name):
        if not os.path.isfile(file_name):
            print(f"The path '{file_name}' is not a file.")
            sys.exit(1)

    curses.wrapper(main)
