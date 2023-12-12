import json

def wordlen(sizes, s):    
    soma = sum([sizes[c] for c in s])
    return soma - len(s)


def getsizes():
    with open('data/sizes.json', 'r') as f:
        sizes = json.load(f)
    return sizes


def text_splitter(texto:str):
    MAXLINE = 660
    NEARMAX = 600

    sizes = getsizes()

    textolista = texto.split('\n')
    for line in textolista:
        if len(line.strip()) == 0:
            textolista.remove(line)

    resultado = list()
    for lines in textolista:
        original = lines.replace('|', '| ')
        target = original.strip()    

        count = 0
        saida = ''
        words = target.split(' ')
        for i in range(len(words)):
            w = words[i]
            wlen = wordlen(sizes, w)        

            quebra = False
            # Quebra por final de sentença ou forçado
            if '?' in w or '!' in w or '|' in w:
                w = w.replace('|', '')
                quebra = True

            # Quebra por estouro
            if count+wlen >= MAXLINE:
                resultado.append(saida.strip())
                saida = w + ' '
                count = wlen         
                if quebra:
                    resultado.append(saida.strip())
                    count = 0
                    saida = ''
            
            # Quebra por quase estouro + conjunção
            elif count+wlen >= NEARMAX and len(w) <= 3 and not quebra:
                resultado.append(saida.strip())
                saida = w + ' '
                count = wlen 

            # Só quebra forçada:
            elif quebra:
                saida = saida + w
                resultado.append(saida.strip())
                count = 0
                saida = ''

            # Não há quebra
            else:         
                saida = saida + w + ' '
                count = count + wlen + sizes[' ']

        if count > 0:           
            resultado.append(saida.strip())

    return resultado
