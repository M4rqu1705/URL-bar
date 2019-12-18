from bs4 import BeautifulSoup
import json
import re
import requests


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


def clean_up(word):
    word = word.strip()                         # Strip whitespace
    word = re.sub(r'[\s]{2,}', ' ' , word)      # Remove excessive inner whitespae
    return word

def capitalize(word):
    if len(word) <= 1:
        return word.upper()
    else:
        return str(word[0].upper() + word[1:].lower())

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
    LANGUAGES = {"af": "Afrikaans", "ga": "Irish", "sq": "Albanian", "it": "Italian", "ar": "Arabic", "ja": "Japanese", "az": "Azerbaijani", "kn": "Kannada", "eu": "Basque", "ko": "Korean", "bn": "Bengali", "la": "Latin", "be": "Belarusian", "lv": "Latvian", "bg": "Bulgarian", "lt": "Lithuanian", "ca": "Catalan", "mk": "Macedonian", "zh-CN": "Chinese Simplified", "ms": "Malay", "zh-TW": "Chinese Traditional", "mt": "Maltese", "hr": "Croatian", "no": "Norwegian", "cs": "Czech", "fa": "Persian", "da": "Danish", "pl": "Polish", "nl": "Dutch", "pt": "Portuguese", "en": "English", "ro": "Romanian", "eo": "Esperanto", "ru": "Russian", "et": "Estonian", "sr": "Serbian", "tl": "Filipino", "sk": "Slovak", "fi": "Finnish", "sl": "Slovenian", "fr": "French", "es": "Spanish", "gl": "Galician", "sw": "Swahili", "ka": "Georgian", "sv": "Swedish", "de": "German", "ta": "Tamil", "el": "Greek", "te": "Telugu", "gu": "Gujarati", "th": "Thai", "ht": "Haitian Creole", "tr": "Turkish", "iw": "Hebrew", "uk": "Ukrainian", "hi": "Hindi", "ur": "Urdu", "hu": "Hungarian", "vi": "Vietnamese", "is": "Icelandic", "cy": "Welsh", "id": "Indonesian", "yi": "Yiddish"}

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


def main():
    word = str(input('[<<] ')).strip().lower()
    #  info = Merriam_Webster_Definitions(word)
    #  info = RAE_Definition(word)
    #  info = WordReference_Synonym(word, True)
    #  info = Thesaurus(word, False)
    #  info = Google_Translate(word, 'auto', 'en')


    print(info.get_title())
    print(info.get_subtitle())
    print(info.get_entries())


if __name__ == '__main__':
    main()
