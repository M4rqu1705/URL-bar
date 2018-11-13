from googletrans import Translator
import urllib
from urllib.request import Request, urlopen
import string
import re
import pyrae
from PyDictionary import PyDictionary
import sys, os

translator = Translator()
rae = pyrae.DLE()
dictionary = PyDictionary()

def translate(text, source, destination):
    try:
        translation = str(translator.translate(text, src=source, dest=destination))
        translation = translation.replace(translation[:translation.find("text=")+5], "").replace(translation[translation.find(", pronunciation="):], "")
    except:
        print("Error. Try again!!")

def define(word):

    try:
        address = "https://www.merriam-webster.com/dictionary/" + word
        headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2"}
        url = Request(address, headers = headers)
        web_page = urlopen(url).read().decode("utf-8","ignore")

        #  definitions = re.findall(r"(?=<div class=\"(?:\.*has-num.*|.*vg.*)>[\S\s]*?<\/div>)[\S\s]*?<strong class=\"mw_t_bc\">: <\/strong>([\S\s]*?)(?=<.*)", web_page) 
        definitions = re.findall(r"<span class=\"dtText\">([\S\s]*?)<\/span>", web_page) 
        c = 0
        for definition in definitions:
            
            # Remove HTML tags in definition
            definition = re.sub("<[^>]*>", "", definition)
            # Remove newlines in definition
            definition = re.sub("\n
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
        print(palabra)
        # Preparar el URI de el pedido con la direccion https y headers apropiados
        direccion = "http://www.wordreference.com/definicion/hola" + str(palabra)
        headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2"}
        url = Request(direccion, headers = headers)

        # Recuperar y extraer partes relevantes de la página
        pagina_web = urlopen(url).read().decode("utf-8","ignore") 
        print(pagina_web) 
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
    try:
        # Prepare the request url with the appropriate http direction and headers
        direction = "https://www.thesaurus.com/browse/" + str(word) + "?s=t"
        headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2"}
        url = Request(direction, headers = headers)

        # Retrieve and decode website with relevant parts only
        web_page = urlopen(url).read().decode("utf-8","ignore")
        web_page = re.findall("<section class=\"synonyms-container.*?</section>", web_page)

        # Find every instance of a synonym in the retrieved website
        synonyms_list = re.findall("<li>.*?</li>", web_page[0])

        # Print out the results in an appealing way
        c = 1
        for synonym in synonyms_list:
            synonym = re.sub(".css.*}|<li>.*<span.*?>|<.*?>", "", synonym).capitalize()
            print("{}) {}".format(c, synonym))
            c += 1

    except:
        print("Error. Check spelling and try again!!")


last_action = "quit"
actions = {"translate":r"^(?:translate|traducir) *", "define":r"^(?:define|dict|dictionary) *",
            "definir":r"^(?:definir|dicc|diccionario) *", "tesauro":r"^(?:tesauro|sinonimo|sin|antonimo|anto) *", 
            "thesaurus":r"^(?:thesaurus|synonym|syn|anthonym|antho) *", "clear":r"^(?:clear|cls)",
            "exit":r"^(?:quit|exit)"}
screen_size = [0,0]


#scroll or table to display results
#color?
if __name__=="__main__":

    
    
    #  os.system('cls')
    while(True):

        try:
            screen_size[0], screen_size[1] = os.get_terminal_size(0)
        except OSError:
            screen_size[0], screen_size[1] = os.get_terminal_size(1)


        task = input("[<<] ").lower().strip()
        if re.search(actions["translate"], task) or (last_action == "translate" and not True in [bool(re.search(value, task)) for key, value in actions.items() if key != "translate"]):
            last_action = "translate"
            task = re.sub(r"^(?:translate|traducir)", "", task, flags=re.M)
            translate(task.strip())
            print("_"*screen_size[0] + "\n")

        elif re.search(actions["define"], task) or (last_action == "define" and not True in [bool(re.search(value, task)) for key, value in actions.items() if key != "define"]):
            last_action = "define"
            task = re.sub(r"^(?:define|dict|dictionary)", "", task, flags=re.M)
            define(task.strip())
            print("_"*screen_size[0] + "\n")

        elif re.search(actions["definir"], task) or (last_action == "definir" and not True in [bool(re.search(value, task)) for key, value in actions.items() if key != "definir"]):
            last_action = "definir"
            task = re.sub(r"^(?:definir|dicc|diccionario)", "", task, flags=re.M)
            definir(task.strip())
            print("_"*screen_size[0] + "\n")

        elif re.search(actions["tesauro"], task) or (last_action == "tesauro" and not True in [bool(re.search(value, task)) for key, value in actions.items() if key != "tesauro"]):
            last_action = "tesauro"
            task = re.sub(r"^(?:tesauro|sinonimo|sin|antonimo|anto)", "", task, flags=re.M)
            sinonimo(task.strip())
            print("_"*screen_size[0] + "\n")

        elif re.search(actions["thesaurus"], task) or (last_action == "thesaurus" and not True in [bool(re.search(value, task)) for key, value in actions.items() if key != "thesaurus"]):
            last_action = "thesaurus"
            task = re.sub(r"^(?:thesaurus|synonym|syn|anthonym|antho) *", "", task, flags=re.M)
            synonym(task.strip())
            print("_"*screen_size[0] + "\n")

        elif re.search(actions["clear"], task) or (last_action == "clear" and not True in [bool(re.search(value, task)) for key, value in actions.items() if key != "clear"]):
            last_action = "clear"
            os.system('cls')

        elif re.search(actions["exit"], task) or (last_action == "exit" and not True in [bool(re.search(value, task)) for key, value in actions.items() if key != "exit"]):
            print("_"*screen_size[0] + "\n")
            os._exit(0)


