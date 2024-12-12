

def handle_backspace(state):
    index_x = state.cursor_x + state.view_x
    index_y = state.cursor_y + state.view_y
    if index_x > 0:
        state.text[index_y] = state.text[index_y][:index_x - 1] \
            + state.text[index_y][index_x:]
        state.set_cursor_x(state.cursor_x - 1)
    elif index_y > 0:
        state.set_cursor_x(state.cursor_x - 1)
        state.text[index_y - 1] += state.text[index_y]
        state.text.pop(index_y)
    state.reset_select()


def handle_delete(state):
    index_x = state.cursor_x + state.view_x
    index_y = state.cursor_y + state.view_y
    if index_x < len(state.text[index_y]):
        state.text[index_y] = state.text[index_y][:index_x] \
            + state.text[index_y][index_x + 1:]
    elif index_y + 1 < len(state.text):
        state.text[index_y] += state.text[index_y + 1]
        state.text.pop(index_y + 1)
    state.reset_select()


def handle_enter(state):
    index_x = state.cursor_x + state.view_x
    index_y = state.cursor_y + state.view_y
    new_line = state.text[index_y][index_x:]
    state.text[index_y] = state.text[index_y][:index_x]
    s = state.text[index_y]
    spaces_len = len(s) - len(s.lstrip(' '))
    spaces = ' ' * spaces_len
    state.text.insert(index_y + 1, spaces + new_line)
    state.set_cursor_x(state.cursor_x + spaces_len + 1)
    state.reset_select()


def handle_all_keys(state, key):
    char = chr(key)
    if char == '\t':
        char = '    '
    index_x = state.cursor_x + state.view_x
    index_y = state.cursor_y + state.view_y
    state.text[index_y] = state.text[index_y][:index_x] + char + state.text[index_y][index_x:]
    state.set_cursor_x(state.cursor_x + len(char))
    state.reset_select()

