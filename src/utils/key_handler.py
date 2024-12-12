

def handle_backspace(state):
    if state.any_selected():
        state.delete_selected()
        return
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


def handle_delete(state):
    if state.any_selected():
        state.delete_selected()
        return
    index_x = state.cursor_x + state.view_x
    index_y = state.cursor_y + state.view_y
    if index_x < len(state.text[index_y]):
        state.text[index_y] = state.text[index_y][:index_x] \
            + state.text[index_y][index_x + 1:]
    elif index_y + 1 < len(state.text):
        state.text[index_y] += state.text[index_y + 1]
        state.text.pop(index_y + 1)


def handle_enter(state):
    state.delete_selected()
    index_x = state.cursor_x + state.view_x
    index_y = state.cursor_y + state.view_y
    new_line = state.text[index_y][index_x:]
    state.text[index_y] = state.text[index_y][:index_x]
    s = state.text[index_y]
    spaces_len = len(s) - len(s.lstrip(' '))
    spaces = ' ' * spaces_len
    state.text.insert(index_y + 1, spaces + new_line)
    state.set_cursor_x(state.cursor_x + spaces_len + 1)


def handle_all_keys(state, key):
    state.delete_selected()
    char = chr(key)
    if char == '\t':
        char = '    '
    index_x = state.cursor_x + state.view_x
    index_y = state.cursor_y + state.view_y
    state.text[index_y] = state.text[index_y][:index_x] + char + state.text[index_y][index_x:]
    state.set_cursor_x(state.cursor_x + len(char))

