from bs4 import BeautifulSoup
import curses
import curses.textpad
import json
import re
import requests

import locale
locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()


#     ___ _      _   ___ ___     ___  ___ ___ ___ _  _ ___ _____ ___ ___  _  _ ___ 
#    / __| |    /_\ / __/ __|   |   \| __| __|_ _| \| |_ _|_   _|_ _/ _ \| \| / __|
#   | (__| |__ / _ \\__ \__ \   | |) | _|| _| | || .` || |  | |  | | (_) | .` \__ \
#    \___|____/_/ \_\___/___/   |___/|___|_| |___|_|\_|___| |_| |___\___/|_|\_|___/
#                                                                                  

# Information is extracted within these classes:
class Information:
    title = ''
    subtitle = ''
    entries = ''

    def __init__(self):
        self.title = ''
        self.subtitle = ''
        self.entries = []

    def set_title(self, title):
        self.title = title.strip().upper()
    def get_title(self):
        return self.title

    def set_subtitle(self, subtitle):
        self.subtitle = subtitle.strip().upper()
    def get_subtitle(self):
        return self.subtitle

    def set_entries(self, entries):
        self.entries = entries
    def get_entries(self):
        return self.entries


# Body object for the curses TUI
# Mostly automates scrolling and makes it easier to insert a message and format
# it automatically
class Body:
    def __init__(self, max_y=10, max_x=10, beg_y=0, beg_x=0, wrapped_line_prefix='... '):
        self.y0 = beg_y
        self.x0 = beg_x
        self.max_y = max_y
        self.max_x = max_x
        self.wrapped_line_prefix = wrapped_line_prefix

        self.message = ''
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


# Text box object for the curses TUI
# Mainly automates validation and preparation of user input string INCLUDING
# non-ascii characters and interpreting other uniquely
class TextBox:
    def __init__(self, max_x, beg_y, beg_x, body, process_query):
        win = curses.newwin(1, max_x, beg_y, beg_x)
        self.win = curses.textpad.Textbox(win)
        self.win.stripspaces = False
        self.win.insert_mode = True
        self.user_input = ''
        self.body = body
        self.process_query = process_query

    def validate(self, char):
        # Make sure that accents are taken into account
        #  curses.endwin(); breakpoint()
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
            response = self.process_query(self.gather())
            if isinstance(response, str):
                if response == 'clear':
                    self.clear()
            else:
                return response
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
        self.user_input = ''
        self.win.win.clear()

    def gather(self):
        return self.user_input


#    _  _ ___ _    ___ ___ ___     ___ _   _ _  _  ___ _____ ___ ___  _  _ ___ 
#   | || | __| |  | _ \ __| _ \   | __| | | | \| |/ __|_   _|_ _/ _ \| \| / __|
#   | __ | _|| |__|  _/ _||   /   | _|| |_| | .` | (__  | |  | | (_) | .` \__ \
#   |_||_|___|____|_| |___|_|_\   |_|  \___/|_|\_|\___| |_| |___\___/|_|\_|___/
#                                                                              
# Clean up strings
def clean_up(word):
    word = word.strip()                         # Strip whitespace
    word = re.sub(r'[\s]{2,}', ' ' , word)      # Remove excessive inner whitespae
    return word

# Capitalize strings
def capitalize(word):
    if len(word) <= 1:
        return word.upper()
    else:
        return str(word[0].upper() + word[1:].lower())

# Prepare basic template for application TUI
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
    text_box = TextBox(text_width, 1, 8, body, process_query)

    # Close the bottom part of the box
    screen.addstr(max_y-2, 1, '└' + '─'*(content_width+1) + '┘')

    return screen, text_box, body


#    ___ _   _ _  _  ___ _____ ___ ___  _  _     ___  ___ ___ ___ _  _ ___ _____ ___ ___  _  _ ___ 
#   | __| | | | \| |/ __|_   _|_ _/ _ \| \| |   |   \| __| __|_ _| \| |_ _|_   _|_ _/ _ \| \| / __|
#   | _|| |_| | .` | (__  | |  | | (_) | .` |   | |) | _|| _| | || .` || |  | |  | | (_) | .` \__ \
#   |_|  \___/|_|\_|\___| |_| |___\___/|_|\_|   |___/|___|_| |___|_|\_|___| |_| |___\___/|_|\_|___/
#                                                                                                  
def Merriam_Webster_Definitions(word):
    word = word.strip().lower()

    info = Information()
    info.set_title(word)

    url = f'https://www.merriam-webster.com/dictionary/{word}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    bs4_entry_headers = soup.select('div.entry-header')
    bs4_entries = soup.select('div[id^="dictionary-entry"]')

    output = ''

    # Iterate over every entry including an index of iteration
    for i, bs4_entry in enumerate(bs4_entries):
        part_of_speech = bs4_entry_headers[i]
        part_of_speech = part_of_speech.select_one('span.fl')
        part_of_speech = clean_up(part_of_speech.get_text())
        part_of_speech = capitalize(part_of_speech)

        if len(output) != 0:
            output += '\n'
        output += f'Part of Speech: {part_of_speech}\n'

        bs4_definitions = bs4_entry.select('span.dtText')
        for bs4_definition in bs4_definitions:
            try:
                for colon in bs4_definition.select('strong.mw_t_bc'):
                    colon.decompose()
            except Exception:
                pass

            # Try to extract any example sentences inside definition
            bs4_examples = []
            try:
                for bs4_example in bs4_definition.select('span.ex-sent'):
                    bs4_examples.append(bs4_example)
            except Exception:
                pass

            # Decomposition order matters, so I am extracting examples before decomposing them from soup object
            examples = ''
            for bs4_example in bs4_examples:
                example = clean_up(bs4_example.get_text())
                example = capitalize(example)
                if re.match(r'^— \w+', example):            # If matches an author quote
                    example = example.strip().title()
                examples += f'    ○ {example}\n'

            for bs4_example in bs4_definition.select('span.ex-sent'):
                bs4_example.decompose()
            definition = clean_up(bs4_definition.get_text())
            definition = definition.capitalize()

            output += f'  ● {definition}\n'
            output += examples

        info.set_entries(output)
    return info


def RAE_Definition(word):
    word = word.strip().lower()

    info = Information()
    info.set_title(word)

    url = f'https://dle.rae.es/{word}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    bs4_definitions = soup.select('div#resultados > article > p')

    output = ''
    # Iterar por cada definición e incluir un índice
    for i, bs4_definition in enumerate(bs4_definitions):
        definition = clean_up(bs4_definition.get_text())

        # La primera entrada siempre tiene el origen de la palabra
        if i == 0:
            info.set_subtitle(f'{definition}')
        # Uso de una palabra
        elif not re.match(r'^\d+\. \w+\.', definition):
            if len(output) != 0:
                output += '\n'
            output += f'Uso: {definition}\n'
        # Definición como tal
        else:
            definition = re.sub(r'^\d+\. ', '', definition)
            output += f'  ● {definition}\n'

    info.set_entries(output)

    return info


def Thesaurus(word, search_synonym=True):
    def fix_json(string):
        # Thank you https://stackoverflow.com/questions/18514910/how-do-i-automatically-fix-an-invalid-json-string
        string = string[:-2]
        string = '{' + string + '}'

        while True:
            try:
                json.loads(string)              # try to parse...
                return string                   # parsing worked -> exit loop
            except Exception as e:
                # Insert expected characters
                result = re.search(r"Expecting '(.+)' delimiter.*\(char (\d+)\)", str(e))
                char, pos = result.group(1), int(result.group(2))
                string = string[:pos] + char + string[pos:]

    word = word.strip().lower()

    info = Information()
    info.set_title(word)

    url = f'https://www.thesaurus.com/browse/{word}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    data = ''
    bs4_scripts = soup.select('script')
    for bs4_script in bs4_scripts:
        script = clean_up(bs4_script.get_text())
        if re.match(r'^window\.INITIAL_STATE = \{', script):
            script = re.sub(r'^window\.INITIAL_STATE = \{', '', script)
            script = fix_json(script)
            data = json.loads(script)

            ''' JSON data is retrieved like:
            dictionary['searchData']
                    1) ['searchTerm']
                    2) ['tunaApiData']
                            a) ['entry'] == 1
                            b) ['posTabs'] = list of dicionaries
                                    i) ['isInformal'] = IDK
                                    ii) ['isVulgar'] = int
                                    iii) ['definition']
                                    iv) ['pos'] = Part of speech
                                    v) ['synonyms'] = list of dictionaries
                                            - ['similarity'] = int
                                            - ['isVulgar']
                                            - ['isInformal'] = int
                                            - ['term']
                                    vi) ['antonyms']
                                            - ['similarity'] = negative intjkjkjkj
                                            - ['isVulgar']
                                            - ['isInformal'] = int
                                            - ['term']
            '''

    output = ''
    for tab in data['searchData']['tunaApiData']['posTabs']:
        output += f'Definition: {tab["definition"]}\n'
        output += f'Part of Speech: {tab["pos"]}\n'

        _nyms = []
        if search_synonym:
            for synonym in tab['synonyms']:
                similarity = int(synonym['similarity'])
                synonym = clean_up(synonym['term'])
                _nyms.append([similarity, synonym])
        else:
            for antonym in tab['antonyms']:
                similarity = abs(int(antonym['similarity']))
                antonym = clean_up(antonym['term'])
                _nyms.append([similarity, antonym])

        # Sort synonyms or antonyms on decreasing similarity
        _nyms = sorted(_nyms, key=lambda x: x[0], reverse=True)

        for _nym in _nyms:
            similarity = _nym[0]
            nym = _nym[1]

            output += '  '
            if 75 < similarity <= 100:
                output += '█'
            elif 50 < similarity <= 75:
                output += '▓'
            elif 25 < similarity <= 50:
                output += '▒'
            elif 0 < similarity <= 25:
                output += '░'
            output += f' {nym}\n'

    info.set_entries(output)

    return info


def WordReference_Synonym(word, search_synonym=True):
    word = word.strip().lower()

    info = Information()
    info.set_title(word)

    url = f'https://www.wordreference.com/sinonimos/{word}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')


    output = ''
    _nyms = []
    if search_synonym:
        _nyms = soup.select('div#article > div.trans > ul > li')
    else:
        _nyms = soup.select('div#article > div.trans > ul > ul > li')

    # Iterar por cada lista de sinónimos e incluir un índice
    for i, bs4_nym in enumerate(_nyms):
        _nyms = clean_up(bs4_nym.get_text())
        _nyms = re.sub('\s?,\s?', ',', _nyms)
        _nyms = _nyms.split(',')

        if len(output) != 0:
            output += '\n'
        output += f'Entrada: {i+1}\n'

        for _nym in _nyms:
            # Remover "Antónimos" u otras palabras similares del inicio
            if re.match(r'^\w+: \w+', _nym):
                _nym = re.sub(r'^\w+: ', '', _nym)
            _nym = capitalize(_nym)
            output += f'  ● {_nym}\n'



    info.set_entries(output)

    return info


def Google_Translate(word, source, target):
    word = clean_up(word).lower()
    source = clean_up(source).lower()
    target = clean_up(target).lower()

    url = f'https://translate.google.com/translate_a/single?client=gtx&sl={source}&tl={target}&dj=1&dt=bd&q={word}'
    response = requests.get(url)

    # Dictionary to convert abbreviation to actual language
    # Taken from 'https://ctrlq.org/code/19899-google-translate-languages'
    LANGUAGES = {'af': 'Afrikaans', 'ga': 'Irish', 'sq': 'Albanian', 'it': 'Italian', 'ar': 'Arabic', 'ja': 'Japanese', 'az': 'Azerbaijani', 'kn': 'Kannada', 'eu': 'Basque', 'ko': 'Korean', 'bn': 'Bengali', 'la': 'Latin', 'be': 'Belarusian', 'lv': 'Latvian', 'bg': 'Bulgarian', 'lt': 'Lithuanian', 'ca': 'Catalan', 'mk': 'Macedonian', 'zh-CN': 'Chinese Simplified', 'ms': 'Malay', 'zh-TW': 'Chinese Traditional', 'mt': 'Maltese', 'hr': 'Croatian', 'no': 'Norwegian', 'cs': 'Czech', 'fa': 'Persian', 'da': 'Danish', 'pl': 'Polish', 'nl': 'Dutch', 'pt': 'Portuguese', 'en': 'English', 'ro': 'Romanian', 'eo': 'Esperanto', 'ru': 'Russian', 'et': 'Estonian', 'sr': 'Serbian', 'tl': 'Filipino', 'sk': 'Slovak', 'fi': 'Finnish', 'sl': 'Slovenian', 'fr': 'French', 'es': 'Spanish', 'gl': 'Galician', 'sw': 'Swahili', 'ka': 'Georgian', 'sv': 'Swedish', 'de': 'German', 'ta': 'Tamil', 'el': 'Greek', 'te': 'Telugu', 'gu': 'Gujarati', 'th': 'Thai', 'ht': 'Haitian Creole', 'tr': 'Turkish', 'iw': 'Hebrew', 'uk': 'Ukrainian', 'hi': 'Hindi', 'ur': 'Urdu', 'hu': 'Hungarian', 'vi': 'Vietnamese', 'is': 'Icelandic', 'cy': 'Welsh', 'id': 'Indonesian', 'yi': 'Yiddish'}

    data = json.loads(response.text)

    info = Information()
    info.set_title(word)
    info.set_subtitle(LANGUAGES[data['src']] + ' to ' + LANGUAGES[target])

    data = data['dict'][0]

    output = ''
    max_score = max([e['score'] for e in data['entry']])

    if len(output) != 0:
        output += '\n'

    output += f'Part of Speech: {data["pos"]}\n'

    for entry in data['entry']:
        performance = (entry['score'] / max_score)*100
        output += '  '
        if 75 < performance <= 100:
            output += '█'
        elif 50 < performance <= 75:
            output += '▓'
        elif 25 < performance <= 50:
            output += '▒'
        elif 0 < performance <= 25:
            output += '░'

        output += f' {entry["word"]} - '
        output += ', '.join(entry['reverse_translation'])
        output += '\n'

    info.set_entries(output)

    return info


def curses_ui(screen):
    global message
    screen, text_box, body = basic_template(screen)

    screen.refresh()
    text_box.refresh()
    body.refresh()


    text_box.edit()

def process_query(query):
    if query == 'exit':
        return 10
    else:
        print(query)
        return 'clear'


if __name__ == '__main__':
    curses.wrapper(curses_ui)