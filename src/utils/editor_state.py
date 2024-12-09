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
        d = position - self.cursor_x
        if d < 0:
            d = abs(d)
            if self.cursor_x - d < 0:
                while self.view_y > 0 and d > 0:
                    d -= 1
                    self.set_cursor_y(self.cursor_y - 1)
                    line_size = len(self.text[self.view_y + self.cursor_y])
                    self.cursor_x = line_size
                    self.cursor_x -= min(line_size, d)
                    d -= min(line_size, d)
            else:
                self.cursor_x -= d
        elif d > 0:
            if self.cursor_x + d > len(self.text[self.view_y + self.cursor_y]):
                file_end = len(self.text) - 1
                while self.view_y + self.cursor_y < file_end and d > 0:
                    d -= 1
                    self.set_cursor_y(self.cursor_y + 1)
                    line_size = len(self.text[self.view_y + self.cursor_y])
                    self.cursor_x = 0
                    self.cursor_x += min(line_size, d)
                    d -= min(line_size, d)
            else:
                self.cursor_x += d
    

    def set_cursor_y(self, position):
        d = position - self.cursor_y
        if d < 0:
            d = abs(d)
            if self.cursor_y >= d:
                self.cursor_y -= d
            else:
                view_d = self.cursor_y + d
                self.cursor_y = 0
                self.view_y = max(0, self.view_y - view_d)
        elif d > 0:
            screen_end = len(self.view_port) - 1
            file_end = len(self.text) - 1
            if self.cursor_y + d <= screen_end:
                self.cursor_y += d
            else:
                view_d = self.cursor_y + d - screen_end
                self.cursor_y = screen_end
                self.view_y = min(file_end, self.view_y + view_d)
        try:
            self.cursor_x = min(self.cursor_x, len(self.text[self.view_y + self.cursor_y]))
        except:
            self.cursor_x = 0


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
        width = self.width
        number_bar_width = self.number_bar_width
        for idx, line in enumerate(self.view_port):
            line_number = idx + self.view_y + 1
            trimmed_line = line[:width - number_bar_width]
            line_number = str(line_number).rjust(number_bar_width - 1) + ' '
            if not self.show_line_numbers:
                line_number = ''
            line_to_display = f'{line_number}{trimmed_line}'
            self.draw_line_to_screen(line_to_display, idx)


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
        col_position = self.cursor_x + 1
        mode_and_position = f"{mode_or_cmd} Line: {row_position}, Col: {col_position}"
        self.draw_line_to_screen(f"File: {self.file_name[:self.width - 6]}", self.height - 2)
        self.draw_line_to_screen(mode_and_position, self.height - 1)
    

    def draw_line_to_screen(self, line, index):
        self.stdscr.addstr(index, 0, line)
        


