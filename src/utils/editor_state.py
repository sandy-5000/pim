import curses


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
            while self.view_y + self.cursor_y > 0 and d > 0:
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
            while self.view_y + self.cursor_y > 0 and d > 0:
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
            return


    def set_cursor_y(self, position):
        d = position - self.cursor_y
        if d < 0:
            d = abs(d)
            self.cursor_y -= d
            self.adjust_view()
            # if self.view_y + self.cursor_y >= d:
            # else:
            #     view_d = self.cursor_y + d
            #     self.cursor_y = 0
            #     self.view_y = max(0, self.view_y - view_d)
        elif d > 0:
            self.cursor_y += d
            self.adjust_view()
            # file_end = len(self.text) - 1
            # screen_end = len(self.view_port) - 1 - self.cursor_y
            # if self.view_y + self.cursor_y + d <= screen_end:
            # else:
            #     view_d = self.cursor_y + d - screen_end
            #     self.cursor_y = screen_end
            #     self.view_y = min(file_end, self.view_y + view_d)
        try:
            line_size = len(self.text[self.view_y + self.cursor_y])
            self.cursor_x = min(self.cursor_x, line_size - self.view_x)
            if self.cursor_x < 0:
                self.view_x += self.cursor_x
                self.cursor_x = 0
        except:
            self.view_x = 0
            self.cursor_x = 0

    def adjust_view(self):
        if self.cursor_y < 0:
            print('cane')
            self.view_y += self.cursor_y
            self.view_y = max(0, self.view_y)
            self.cursor_y = 0
        elif self.cursor_y > len(self.view_port) - 1:
            self.view_y += self.cursor_y - len(self.view_port) + 1
            self.view_y = min(self.view_y, len(self.text) - 1)
            self.cursor_y = len(self.view_port) - 1
            print(self.view_y, self.cursor_y)
        left_pad = 0
        if self.show_line_numbers:
            left_pad = self.number_bar_width
        if self.cursor_x < 0:
            self.view_x += self.cursor_x
            self.cursor_x = 0
            self.view_x = max(0, self.view_x)
        elif self.cursor_x > self.width - left_pad:
            self.view_x += self.width - left_pad - self.cursor_x
            self.cursor_x = self.width - left_pad
            self.view_x = min(self.view_x, len(self.text[self.view_y + self.cursor_y]))


    def move_cursor(self, key):
        match key:
            case curses.KEY_UP:
                self.set_cursor_y(self.cursor_y - 1)
            case curses.KEY_DOWN:
                self.set_cursor_y(self.cursor_y + 1)
            case curses.KEY_LEFT:
                self.set_cursor_x(self.cursor_x - 1)
            case curses.KEY_RIGHT:
                self.set_cursor_x(self.cursor_x + 1)


    def refresh(self):
        height, width = self.stdscr.getmaxyx()
        self.height = height
        self.width = width - 1
        self.view_port_height = self.height - 2
        self.number_bar_width = len(str(len(self.text))) + 1
        self.adjust_view()

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

