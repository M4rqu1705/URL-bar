import curses
import curses.textpad
import locale
locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()

class Body:
    def __init__(self, max_y=10, max_x=10, beg_y=0, beg_x=0, wrapped_line_prefix='... '):
        self.y0 = beg_y
        self.x0 = beg_x
        self.max_y = max_y
        self.max_x = max_x
        self.wrapped_line_prefix = wrapped_line_prefix

        self.message = ""
        self.abs_scroll = 0


        self.win = curses.newwin(self.max_y, self.max_x, self.y0, self.x0)

    def set_message(self, message):
        import textwrap
        wrapper = textwrap.TextWrapper(
                width=self.max_x,
                tabsize=4,
                replace_whitespace=False,
                drop_whitespace=False,
                subsequent_indent=self.wrapped_line_prefix)
        self.message = wrapper.wrap(message)

    def refresh(self):
        self.win.refresh()

    def clear(self):
        self.win.clear()

    def scroll_body(self, scroll_increment):
        # Clear body to remove garbage from previous view
        self.clear()

        # If scroll is not more than 2 lines below text boundary
        if not 2 < (self.max_y + self.abs_scroll + scroll_increment) - len(self.message):
            # Increase absolute scroll by scroll increment units
            self.abs_scroll += scroll_increment

        # Make sure scroll is not above text boundary
        if self.abs_scroll < 0:
            self.abs_scroll = 0
            
        # Restrain amount of lines in message based on abs_scroll and max_y
        message = self.message[self.abs_scroll:self.abs_scroll+self.max_y-1]

        # Add lines to screen
        for i,line in enumerate(message):
            self.win.addstr(i, 0, line)


class TextBox:
    def __init__(self, max_x, beg_y, beg_x, body):
        win = curses.newwin(1, max_x, beg_y, beg_x)
        self.win = curses.textpad.Textbox(win)
        self.win.stripspaces = False
        self.win.insert_mode = True
        self.user_input = ''
        self.body = body

    def validate(self, char):
        # Make sure that accents are taken into account
        if char == 259:         # Up arrow
            self.body.scroll_body(-1)
            self.body.refresh()
        elif char == 258:       # Down arrow
            self.body.scroll_body(1)
            self.body.refresh()
        elif char == 260:       # Left arrow
            cursor = self.win.win.getyx()[1]
            if cursor-1 < 0:
                return 0
            else:
                return char
        elif char == 261:       # Right arrow
            cursor = self.win.win.getyx()[1]
            if cursor+1 > len(self.user_input):
                return 0
            else:
                return char
        elif char == 262:       # Home key
            self.win.win.move(0,0)
            return char
        elif char == 358:        # End key
            self.win.win.move(0,len(self.user_input))
            return char
        elif char == 10:        # Enter
            return char
        elif char == 8:         # Backspace
            cursor = self.win.win.getyx()[1]
            self.user_input = self.user_input[:cursor-1] + self.user_input[cursor:]
            return char
        elif char == 330:
            cursor = self.win.win.getyx()[1]
            self.user_input = self.user_input[:cursor] + self.user_input[cursor+1:]
            # Delete character under cursor
            self.win.do_command(4)
            return char
        elif char == 225:       # á
            self.user_input += 'á'
            return ord('a')
        elif char == 193:       # Á
            self.user_input += 'Á'
            return ord('A')
        elif char == 233:       # é
            self.user_input += 'é'
            return ord('e')
        elif char == 201:       # É
            self.user_input += 'É'
            return ord('E')
        elif char == 237:       # í
            self.user_input += 'í'
            return ord('i')
        elif char == 205:       # Í
            self.user_input += 'Í'
            return ord('I')
        elif char == 243:       # ó
            self.user_input += 'ó'
            return ord('o')
        elif char == 211:       # Ó
            self.user_input += 'Ó'
            return ord('O')
        elif char == 250:       # ú
            self.user_input += 'ú'
            return ord('u')
        elif char == 218:       # Ú
            self.user_input += 'Ú'
            return ord('U')
        elif char == 241:       # ñ
            self.user_input += 'ñ'
            return ord('n')
        elif char == 209:       # Ñ
            self.user_input += 'Ñ'
            return ord('N')
        elif char == 252:       # ü
            self.user_input += 'ü'
            return ord('u')
        elif char == 220:       # Ü
            self.user_input += 'Ü'
            return ord('U')
        elif char == 161:       # ¿
            self.user_input += '¿'
            return ord('?')
        elif char == 191:       # ¡
            self.user_input += '¡'
            return ord('!')
        else:
            cursor = self.win.win.getyx()[1]
            self.user_input = self.user_input[:cursor] + chr(char) + self.user_input[cursor:]
            return char

    def edit(self):
        self.win.edit(self.validate)

    def refresh(self):
        self.win.win.refresh()

    def clear(self):
        self.win.clear()

    def gather(self):
        return self.user_input


def basic_template(screen):
    #  global message
    max_y, max_x = screen.getmaxyx()


    # Open text area box and prepare universal variable
    content_width = max_x - 5
    screen.addstr(0, 1, '┌' + '─'*(content_width+1) + '┐')

    # Set up text area
    text_width = content_width - 5
    screen.addstr(1, 1, '│ [<<] ' + ' '*text_width + '│')

    # Both close text area part of input and open "body"  area
    screen.addstr(2, 1, '╞' + '═'*(content_width+1) + '╡')

    # "Body" area
    for y in range(3,max_y-2):
        screen.addstr(y, 1, '│' + ' '*content_width + '▒│')

    # Max_y is substracted 5 to take into acount other lines above and below. The same with content_width
    body = Body(max_y-5, content_width-3, 3, 2)
    text_box = TextBox(text_width, 1, 8, body)

    # Close the bottom part of the box
    screen.addstr(max_y-2, 1, '└' + '─'*(content_width+1) + '┘')

    return screen, text_box, body


def curses_ui(screen):
    global message
    screen, text_box, body = basic_template(screen)

    screen.refresh()
    text_box.refresh()
    body.refresh()


    text_box.edit()

    print(text_box.gather())


curses.wrapper(curses_ui)
