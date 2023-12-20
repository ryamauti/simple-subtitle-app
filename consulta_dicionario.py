import requests

urlbase = f'https://api.dicionario-aberto.net/'

def consulta():
    url = urlbase + 'random'
    r = requests.get(url)
    d = r.json()    
    return d['word']


def significado(word):
    url = urlbase + f'word/{word}'
    r = requests.get(url)
    d = r.json() 
    saida = d[0]['normalized']
    significado = d[0]['xml']
    return saida, significado


def consultanome():
    w = consulta()
    saida, sign = significado(w)
    return saida

