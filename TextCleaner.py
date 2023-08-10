from string import punctuation
import unicodedata

def addSpaces(text):
    newText = ""
    last = ""
    for char in text:
        if last in punctuation:
            newText += " "
        newText += char
        last = char
    return newText

def pretty(text):
    text = unicodedata.normalize("NFKD", text)
    text = addSpaces(text)
    return " ".join(text.split())