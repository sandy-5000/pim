import curses
import pyperclip


class EditorState:
    def __init__(self, stdscr=None):
        self.mode = 'NORMAL'

        self.command = ''
        self.message = ''
        self.buffer = ''

        self.view_x = 0
        self.view_y = 0
        self.cursor_x = 0
        self.cursor_y = 0

        self.height = 0
        self.width = 0

        self.text = ['']
        self.view_port = ['']

        self.view_port_height = 0
        self.show_line_numbers = True
        self.number_bar_width = 2

        self.stdscr = stdscr

        self.file_name = ''


    def set_stdscr(self, stdscr):
        self.stdscr = stdscr


    def set_cursor_x(self, position):
        left_pad = 0
        if self.show_line_numbers:
            left_pad = self.number_bar_width
        d = position - self.cursor_x
        if d < 0:
            d = abs(d)
            while self.view_y + self.cursor_y + self.cursor_x > 0 and d > 0:
                if self.view_x + self.cursor_x < d:
                    d -= self.view_x + self.cursor_x + 1
                    self.set_cursor_y(self.cursor_y - 1)
                    line_size = len(self.text[self.view_y + self.cursor_y])
                    self.cursor_x = line_size
                    if self.cursor_x > self.width - left_pad:
                        self.view_x = self.cursor_x - self.width + left_pad
                        self.cursor_x = self.width - left_pad
                else:
                    self.cursor_x -= d
                    if self.cursor_x < 0:
                        self.view_x += self.cursor_x
                        self.cursor_x = 0
                    d = 0
        elif d > 0:
            file_end = len(self.text) - 1
            line_end = len(self.text[self.view_y + self.cursor_y])
            while self.view_y + self.cursor_y + self.cursor_x < file_end + line_end and d > 0:
                line_size = len(self.text[self.view_y + self.cursor_y])
                if line_size - (self.view_x + self.cursor_x) < d:
                    d -= line_size - (self.view_x + self.cursor_x) + 1
                    self.set_cursor_y(self.cursor_y + 1)
                    self.cursor_x = 0
                    self.view_x = 0
                else:
                    self.cursor_x += d
                    if self.cursor_x > self.width - left_pad:
                        self.view_x += self.cursor_x - self.width + left_pad
                        self.cursor_x = self.width - left_pad
                    d = 0


    def set_cursor_y(self, position):
        d = position - self.cursor_y
        if d < 0:
            d = abs(d)
            self.cursor_y -= d
            if self.cursor_y < 0:
                self.view_y += self.cursor_y
                self.cursor_y = 0
                self.view_y = max(0, self.view_y)
        elif d > 0:
            file_end = len(self.text)
            self.cursor_y = min(self.cursor_y + d, file_end)
            screen_end = len(self.view_port) - 1
            if self.cursor_y > screen_end:
                self.view_y += self.cursor_y - screen_end
                self.cursor_y = screen_end
                self.view_y = min(file_end - self.view_port_height, self.view_y)
        try:
            line_size = len(self.text[self.view_y + self.cursor_y])
            self.cursor_x = min(self.cursor_x, line_size - self.view_x)
            if self.cursor_x < 0:
                self.view_x += self.cursor_x
                self.cursor_x = 0
        except:
            self.view_x = 0
            self.cursor_x = 0


    def move_cursor(self, key):
        match key:
            case curses.KEY_UP:
                self.set_cursor_y(self.cursor_y - 1)
            case curses.KEY_RIGHT:
                self.set_cursor_x(self.cursor_x + 1)
            case curses.KEY_DOWN:
                self.set_cursor_y(self.cursor_y + 1)
            case curses.KEY_LEFT:
                self.set_cursor_x(self.cursor_x - 1)
            case 547:
                self.set_cursor_y(self.cursor_y - 1)
            case 400:
                self.set_cursor_x(self.cursor_x + 1)
            case 548:
                self.set_cursor_y(self.cursor_y + 1)
            case 391:
                self.set_cursor_x(self.cursor_x - 1)


    def refresh(self):
        height, width = self.stdscr.getmaxyx()
        self.height = height
        self.width = width - 1
        self.view_port_height = self.height - 2
        self.number_bar_width = len(str(len(self.text))) + 1

        self.stdscr.clear()
        self.set_view_port()
        self.draw_view_port()
        self.draw_footer()
        line_number_padding = 0
        if self.show_line_numbers:
            line_number_padding = self.number_bar_width
        self.stdscr.move(self.cursor_y, line_number_padding + self.cursor_x)
        self.stdscr.refresh()


    def set_view_port(self):
        start = self.view_y
        end = self.view_y + self.view_port_height
        self.view_port = self.text[start : end]


    def draw_view_port(self):
        for idx, line in enumerate(self.view_port):
            self.draw_line_to_screen(line, idx)


    def draw_footer(self):
        command_width = self.width - 20
        mode_or_cmd = f'-- {self.mode} --'
        if self.mode == 'NORMAL' and self.command:
            mode_or_cmd = self.command
            self.message = ''
        if self.mode == 'NORMAL' and self.message:
            mode_or_cmd = self.message
        width_diff = command_width - len(mode_or_cmd)
        mode_or_cmd = mode_or_cmd + (' ' * width_diff) if width_diff >= 0 else mode_or_cmd[-command_width:]
        row_position = self.cursor_y + self.view_y + 1
        col_position = self.cursor_x + self.view_x + 1
        mode_and_position = f"{mode_or_cmd} Line: {row_position}, Col: {col_position}"
        self.draw_line_to_screen(f"File: {self.file_name[:self.width - 6]}", self.height - 2)
        self.draw_line_to_screen(mode_and_position, self.height - 1)


    def draw_line_to_screen(self, line, index):
        if index < self.view_port_height:
            if self.show_line_numbers:
                line_number = index + self.view_y + 1
                line_number = str(line_number).rjust(self.number_bar_width - 1) + ' '
                length = self.width - self.number_bar_width
                trimmed_line = line[self.view_x: self.view_x + length]
                trimmed_line = line_number + trimmed_line
            else:
                length = self.width
                trimmed_line = line[self.view_x: self.view_x + length]
            self.stdscr.addstr(index, 0, trimmed_line)
        else:
            self.stdscr.addstr(index, 0, line[ : self.width])


    def copy_to_clipboard(self, start, end):
        self.process_segment_range(start, end)


    def cut_to_clipboard(self, start, end):
        self.process_segment_range(start, end, True)


    def process_segment_range(self, start, end, cut_segment=False):
        if start != '' and start != '.':
            try:
                start = int(start)
            except:
                self.message = 'Invalid number format'
                return
        if end != '' and end != '.':
            try:
                end = int(end)
            except:
                self.message = 'Invalid number format'
                return

        text = self.text
        start_x, start_y = 0, 0
        end_x = len(text[-1]) - 1 if text else 0
        end_y = len(text) - 1

        if start == '.':
            start_x = self.view_x + self.cursor_x
            start_y = self.view_y + self.cursor_y
        elif start != '':
            start_y = max(0, start - 1)
            start_x = 0

        if end == '.':
            end_x = self.view_x + self.cursor_x - 1
            end_y = self.view_y + self.cursor_y
        elif end != '':
            end_y = min(end - 1, len(text) - 1)
            end_x = len(text[end_y]) - 1

        if [start_y, start_x] > [end_y, end_x]:
            self.message = 'Invalid Range'
            return
        if cut_segment:
            self.cut_segment(start_x, start_y, end_x, end_y)
        else:
            self.copy_segment(start_x, start_y, end_x, end_y)


    def copy_segment(self, start_x, start_y, end_x, end_y):
        text = self.text
        text_to_copy = ''
        if start_y == end_y:
            text_to_copy = text[start_y][start_x:end_x + 1]
        else:
            for y in range(start_y, end_y + 1):
                if y == end_y:
                    text_to_copy += text[y][:end_x + 1]
                elif y == start_y:
                    text_to_copy += text[y][start_x:] + '\n'
                else:
                    text_to_copy += text[y] + '\n'
        pyperclip.copy(text_to_copy)
        self.set_cursor_y(end_y - self.view_y)
        self.set_cursor_x(end_x + 1 - self.view_x)
        self.message = f'yanked {end_y - start_y + 1} lines.'


    def cut_segment(self, start_x, start_y, end_x, end_y, copy_it=True):
        text_to_cut = ''
        if start_y == end_y:
            text_to_cut = self.text[start_y][start_x:end_x + 1]
            self.text[start_y] = self.text[start_y][:start_x] + self.text[start_y][end_x + 1:]
        else:
            for y in range(start_y, end_y + 1):
                if y == end_y:
                    text_to_cut += self.text[y][:end_x + 1]
                elif y == start_y:
                    text_to_cut += self.text[y][start_x:] + '\n'
                else:
                    text_to_cut += self.text[y] + '\n'
            new_line = self.text[start_y][:start_x] + self.text[end_y][end_x + 1:]
            self.text[start_y:end_y + 1] = [new_line]
        if copy_it:
            pyperclip.copy(text_to_cut)
            self.message = f'removed {end_y - start_y + 1} lines.'
        self.set_cursor_y(start_y - self.view_y)
        self.set_cursor_x(start_x - self.view_x)


    def paste_from_clipboard(self):
        copied_text = pyperclip.paste()
        copied_text = copied_text.replace('\r', '').replace('\t', ' ' * 4)
        index_x = self.cursor_x + self.view_x
        index_y = self.cursor_y + self.view_y
        new_line = self.text[index_y][:index_x] + copied_text + self.text[index_y][index_x:]
        btw_lines = [*new_line.split('\n')]
        self.text = self.text[:index_y] + btw_lines + self.text[index_y + 1:]
        self.set_cursor_x(self.cursor_x + len(copied_text))
