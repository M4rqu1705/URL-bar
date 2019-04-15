#  from PyDictionary import PyDictionary
#  from googletrans import Translator
from urllib.request import Request, urlopen
import os
import pyrae
import re
import thesaurus


#  translator = Translator()
rae = pyrae.DLE()
#  dictionary = PyDictionary()

#  def translate(text, source, destination):
    #  try:
        #  translation = str(translator.translate(text, src=source, dest=destination))
        #  translation = translation.replace(translation[:translation.find("text=")+5], "").replace(translation[translation.find(", pronunciation="):], "")
    #  except:
        #  print("Error. Try again!!")

def define(word):
    # <div id=\"definition-wrapper.*>([\S\s]*)</div>
    # <(.|\n)*?>


    try:
        address = "https://www.merriam-webster.com/dictionary/" + word
        headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2"}
        url = Request(address, headers = headers)

        web_page = urlopen(url).read().decode("utf-8","ignore")

        definition_wrapper = re.search(r"<div id=\"definition-wrapper.*>([\S\s]*)</div>", web_page).group(1)

        text_only = re.sub(r"<(.|\n)*?>", '', definition_wrapper, flags=re.M)

        words = re.findall(r"(\w+)\s*", text_only)

        c, d = 0, 0
        begin_collect = False
        definitions = [[]]

        for word in words:
            c+=1
            if c > 2 and words[c-4] == "Definition" and words[c-3] == "of":
                begin_collect = True

            if re.search(r"^\d+", word):
                definitions.append([])
                word += ") "
                d+=1

            if begin_collect:
                print("{}) {}".format(c, str(word)))
                definitions[d].append(str(word))


        for definition in definitions:
            definition = ' '.join(definition)
            definition = re.sub("\n", "", definition)
            print(definition)


        return

    #  definitions = re.findall(r"(?=<div class=\"(?:\.*has-num.*|.*vg.*)>[\S\s]*?<\/div>)[\S\s]*?<strong class=\"mw_t_bc\">: <\/strong>([\S\s]*?)(?=<.*)", web_page) 

        # I want to be able to extract every definition, its examples, and the corresponding category (noun, adjective, pronoun, etc.)

        definitions = me.findall(r"<div id=\"dictionarymentry-\d{0,2}[\S\s]*?<!-- END <div id=\"entry-\d\"> -->", web_page)
        temp = []
        for definition in definitions:
            temp.append(re.findall(r"<span class=\"dtText\">([\S\s]*?)<\/span>", definition))
        definitions = temp[:]

        # I want to be able to extract a list of lists of categorized definitions

        headers = re.findall(r"<span class=\"fl\"[\S\s]*?<\/div>", web_page)
        temp = []
        for header in headers:
            #  Remove HTML tags in header
            header = re.sub("<[^>]*?>", "", header)
            #  Remove newlines in header
            header = re.sub("\n", "", header) 

            temp.append(header)
        headers = temp[:]

        # I want to be able to extract a list of headers, which are the categories


        # Resulting list of tuples: [(header, [(definition, example), (definition,example)]), [(header, [(definition, example), (definition,example)]), [(header, [(definition, example), (definition,example)])]



        #  examples = re.findall(r"<span class=\"ex-sent[\S\s]*?(?:</span>[\S\s]*?){2}", web_page)

        c = 0
        for definition in definitions:

            # Remove HTML tags in definition
            definition = re.sub("<[^>]*>", "", definition)
            # Remove newlines in definition
            definition = re.sub("\n", "", definition) 
            # Remove beginning colons and whitespace following it
            definition = re.sub("^:[\s]*", "", definition)
            # Remove any strange characters
            definition = re.sub("\s[()]\s", "", definition)

            # Remove any examples
            definition = re.sub("\n[\S\s]*$", "", definition)
            # Remove surrounding whitespace
            definition = definition.strip()
            # Capitalize first letter of definition
            definition = definition.capitalize()
            # Add a trailing period
            definition += "."

            #  definition = definition.strip().capitalize() + "."
            c = c+1
            print ("\n({}) {}".format(str(c), definition))
    except:
        print("Error. Check spelling and try again!!")

def definir(palabra):
    try:
        # Preparar el URI de el pedido con la direccion https y headers apropiados
        direccion = "http://www.wordreference.com/definicion/" + str(palabra)
        headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2"}
        url = Request(direccion, headers = headers)

        # Recuperar y extraer partes relevantes de la página
        pagina_web = urlopen(url).read().decode("utf-8","ignore") 
        pagina_web = re.findall(r"<ol class='entry'[\S\s]*?</ol>", pagina_web)


        lista_definiciones = []
        for entrada in pagina_web:
            lista_definiciones += re.findall(r"<li>([\S\s]*?)(?=.{0,5})(?:<li>|<span class=i)", entrada)

        if len(lista_definiciones) < 1:
            raise Exception("No definitions found")

        c=1
        for definicion in lista_definiciones:
            definicion = re.sub("(?:<?/?li>|<br>|</?span[\S\s]*?>|<|>)", "", definicion)
            definicion = re.sub("[:\"']", "", definicion)
            definicion = re.sub(" {2,}", " ", definicion)
            definicion = definicion.strip().capitalize()

            # Hacer mayuscula cada letra que le sigue a un punto
            temp = re.compile("\. \S")
            temp = temp.finditer(definicion)
            for match in temp:
                word = match.group()
                start_index, end_index = match.span()
                definicion = definicion[:start_index] + word.upper() + definicion[end_index:]

            if len(definicion) < 2:
                continue

            print("{}) {}".format(c, definicion))
            c += 1

    except:
        print("Error. ¡¡Revise su gramática e intente nuevamente!!")

    #  try:
        #  definiciones = str(rae.exact(palabra)).replace("'","").replace("[","").replace("]","").replace("\"","").split("\\n")
        #  definiciones = definiciones[3:len(definiciones)-1]                
        #  aceptarDisplay = "si"
        #  if len(definiciones)>10:
            #  aceptarDisplay = input("¿Mostrar " + str(len(definiciones))+ " respuestas?\n").lower()
            #  
        #  if aceptarDisplay == "si":
            #  for definicion in definiciones:
                #  definicion = definicion.capitalize()
                #  if definicion[0].isdigit()==0:
                    #  definicion="\n-"+definicion
                #  print(definicion)
        #  else:
            #  c = 0
            #  while c<10:
                #  definiciones[c] = definiciones[c].capitalize()
                #  if definiciones[c][0].isdigit()==0:
                    #  definiciones[c]="\n-"+definiciones[c]
                #  print(definiciones[c])
                #  c=c+1
    #  except:
        #  print("Error. Try again!!")

def sinonimo(palabra):
    try:
        # Preparar el URI de el pedido con la direccion https y headers apropiados
        direccion = "http://www.wordreference.com/sinonimos/" + str(palabra)
        headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2"}
        url = Request(direccion, headers = headers)

        # Recuperar y extraer partes relevantes de la página
        pagina_web = urlopen(url).read().decode("utf-8","ignore")
        pagina_web = re.findall("<div id=\"article\">[\S\s]*?<\/div>", pagina_web)

        # Encontar cada instancia de un sinónimo en la página web
        lista_sinonimos = re.findall("(?!(<li><span[\S\s]*?<\/li>))(<li>[\S\s]*?<\/li>)", pagina_web[0])

        # Demostrar los resultados de forma atractiva
        c = 1
        for sinonimo in lista_sinonimos:
            sinonimo = re.sub("Antónimos.*?<|<.*?>", "", sinonimo[1]).capitalize()
            print("{}) {}".format(c, sinonimo))
            c += 1

    except:
        print("Error. Check spelling and try again!!")

def synonym(word):

    # Structure of Word.data:
    # Group: int
    # What is wanted of it ('partOfSpeech, 'meaning', 'syn', 'ant', etc.)
    # Which one ('word', 'relevance', 'length', 'complexity', 'form')

    try:
        # Get word
        word = thesaurus.Word(word)
        groups = word.data

        for group in groups:

            # Print title of group and part of sentence
            print("{} ({})".format(
                group['meaning'].upper().strip(), 
                group['partOfSpeech'].lower().strip()
                )
                )

            current_line = []

            entries = group['syn']
            for entry in entries:
                line = ", ".join(current_line)

                # Constrain synonyms to display to screen width
                if len(line)+len(entry[0])+3 > screen_size[0] and entry != entries[-1]:
                    print(line)
                    current_line = [entry[0]]
                elif entry == entries[-1]:
                    current_line.append(entry[0].lower().strip())
                    print(line)
                else:
                    current_line.append(entry[0].lower().strip())
            print()

    except thesaurus.exceptions.MisspellingError as e:
        print(e)

def antonym(word):

    # Structure of Word.data:
    # Group: int
    # What is wanted of it ('partOfSpeech, 'meaning', 'syn', 'ant', etc.)
    # Which one ('word', 'relevance', 'length', 'complexity', 'form')

    try:
        # Get word
        word = thesaurus.Word(word)
        groups = word.data

        for group in groups:

            try:
                if len(group['ant']) < 1: 
                    continue
            except:
                continue

            # Print title of group and part of sentence
            print("{} ({})".format(
                group['meaning'].upper().strip(), 
                group['partOfSpeech'].lower().strip()
                )
                )

            current_line = []

            entries = group['ant']
            for entry in entries:
                line = ", ".join(current_line)

                # Constrain synonyms to display to screen width
                if len(line)+len(entry[0])+3 > screen_size[0] and entry != entries[-1]:
                    print(line)
                    current_line = [entry[0]]
                elif entry == entries[-1]:
                    current_line.append(entry[0].lower().strip())
                    print(line)
                else:
                    current_line.append(entry[0].lower().strip())
            print()

    except thesaurus.exceptions.MisspellingError as e:
        print(e)


last_action = "define"
actions = {
        "translate":r"^(?:translate|traducir)",
        "define":r"^(?:define|dict|dictionary)",
        "definir":r"^(?:definir|dicc|diccionario)",
        "tesauro":r"^(?:tesauro|sinonimo|sin|antonimo|anto)", 
        "synonym":r"^(?:synonym|syn)",
        "antonym":r"^(?:antonym|anton|ant)",
        "clear":r"^(?:clear|cls)",
        "exit":r"^(?:quit|exit)"
        }
screen_size = [0,0]


#scroll or table to display results
#color?

if __name__=="__main__":

    while(True):

        # Get screen size
        try:
            screen_size[0], screen_size[1] = os.get_terminal_size(0)
        except OSError:
            screen_size[0], screen_size[1] = os.get_terminal_size(1)

        # Receive user command
        _input = input("[<<] ").lower().strip()

        # Retrieve the task from the user command
        task = re.match(r"^(\w+).*$", _input).group(1)

        # If no acceptable task found 
        check_for_task = [bool(re.search(value, task)) for key, value in actions.items()]
        if(not True in check_for_task):
            # ... try to repeat last task
            task = last_action

        # Retrieve the word from the user command
        word = re.search(r"\w+\s*([\S\s]*)$", _input).group(1).lower().strip()

        # Check which action to perform
        if re.search(actions["translate"], task):
            last_action = "translate"
            #  translate(word)
            print("_"*screen_size[0] + "\n")

        elif re.search(actions["define"], task):
            last_action = "define"
            define(word)
            print("_"*screen_size[0] + "\n")

        elif re.search(actions["definir"], task):
            last_action = "definir"
            definir(word)
            print("_"*screen_size[0] + "\n")

        elif re.search(actions["tesauro"], task):
            last_action = "tesauro"
            sinonimo(word)
            print("_"*screen_size[0] + "\n")

        elif re.search(actions["synonym"], task):
            last_action = "synonym"
            synonym(word)
            print("_"*screen_size[0] + "\n")

        elif re.search(actions["antonym"], task):
            last_action = "antonym"
            antonym(word)
            print("_"*screen_size[0] + "\n")

        elif re.search(actions["clear"], task):
            last_action = "clear"
            os.system('cls')

        elif re.search(actions["exit"], task):
            print("_"*screen_size[0] + "\n")
            os._exit(0)
