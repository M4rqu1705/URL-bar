from googletrans import Translator
import urllib
from urllib.request import Request, urlopen
import string
import re
import pyrae
from PyDictionary import PyDictionary
import os

translator = Translator()
rae = pyrae.DLE()
dictionary = PyDictionary()

def translate(text, source, destination):
    try:
        translation = str(translator.translate(text, src=source, dest=destination))
        translation = translation.replace(translation[:translation.find("text=")+5], "").replace(translation[translation.find(", pronunciation="):], "")
        print(translation+"\n__________________________________________________________________________")
    except:
        print("Error. Try again!!")

def define(word):
    try:
        url = "http://"+ "www" + "." + "merriam-webster" + ".com/dictionary/" + word
        webPage = urllib.request.urlopen(url).read().decode("utf-8","ignore") #open the url, read it and change the encoding to utf-8. Needed to use regex on it
        definitions = re.findall("<span> <span class=\"intro-colon\">:</span>(.+?)</span>", webPage) #regex finds all occurences of the specific
        c = 0
        for definition in definitions:
            definition = definition[2:]
            definition = re.sub("<.*?>", "", definition).capitalize() + "."
            c = c+1
            print (str(c)+") "+definition)
    except:
        print("Error. Check spelling and try again!!")
    print("__________________________________________________________________________\n")


def definir(palabra):
    try:
        definiciones = str(rae.exact(palabra)).replace("'","").replace("[","").replace("]","").replace("\"","").split("\\n")
        definiciones = definiciones[3:len(definiciones)-1]                
        aceptarDisplay = "si"
        if len(definiciones)>10:
            aceptarDisplay = input("¿Mostrar " + str(len(definiciones))+ " respuestas?\n").lower()
            
        if aceptarDisplay == "si":
            for definicion in definiciones:
                definicion = definicion.capitalize()
                if definicion[0].isdigit()==0:
                    definicion="\n-"+definicion
                print(definicion)
        else:
            c = 0
            while c<10:
                definiciones[c] = definiciones[c].capitalize()
                if definiciones[c][0].isdigit()==0:
                    definiciones[c]="\n-"+definiciones[c]
                print(definiciones[c])
                c=c+1
    except:
        print("Error. Try again!!")
    print("__________________________________________________________________________\n")

def sinonimo(palabra):
    try:
        url = Request(("http://www.sinonimos.com/sinonimo.php?palabra=" + str(palabra)), headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2"})
        paginaWeb = urlopen(url).read().decode("utf-8","ignore")
        sinonimos = re.findall("<td width=\"371\" class=\"arial-12-noir\">(.+?)</td>", paginaWeb)
        c = 0
        for sinonimo in sinonimos:
            sinonimo = re.sub("<.*?>", "", sinonimo).capitalize() + "."
            c = c+1
            print (str(c)+") "+sinonimo)
    except:
        print("Error. Check spelling and try again!!")
    print("__________________________________________________________________________\n")

def synonym(word):
    try:
        synonymsList = dictionary.synonym(word)
        synonyms=""
        for synonym in synonymsList:
            synonyms = synonyms+synonym+", "
        print(synonyms[:len(synonyms)-2])
    except:
        print("Error. Check spelling and try again!!")
    print("__________________________________________________________________________\n")




while(1):
    task = input().lower()
    if "translate" in task:
        translate(task[16:], task[10:12], task[13:15])
    elif "traducir" in task:
        translate(task[15:], task[9:11], task[12:14])
    elif "define" in task:
        define(task[7:])
    elif "definir" in task:
        definir(task[8:])
    elif ("sinonimo" or "sinónimo") in task:
        sinonimo(task[9:])
    elif "synonym" in task:
        synonym(task[8:])
    elif ("clear" or "cls") in task:
        os.system('cls')
