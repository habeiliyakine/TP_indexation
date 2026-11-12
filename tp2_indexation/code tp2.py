import re
import math

#1
documents = { }

stopwords = {
"le", "la", "les", "un", "une",
"de", "des", "du", "et", "dans",
"par", "pour", "d", "l"
} 
with open("document.tsv", "r", encoding="utf-8") as fichier:
    for ligne in fichier:
        doc_id, contenu = ligne.strip().split("\t", 1)
        documents[doc_id] = contenu

for doc_id, contenu in documents.items():
    print(doc_id, ":", contenu)
      
def tokeniser(texte):
    return re.findall(r"\b\w+\b", texte.lower())

def supprimer_stopwords(tokens):
    resultat = []

    for token in tokens:
        if token not in stopwords:
            resultat.append(token)

    return resultat

def preprocess(texte):
    tokens = tokeniser(texte)
    tokens = supprimer_stopwords(tokens)
    return tokens

#2
def construire_index(documents):
    index_inverse = {}

    for doc_id, texte in documents.items():
        termes = preprocess(texte)

        for terme in set(termes):
            if terme not in index_inverse:
                index_inverse[terme] = []

            index_inverse[terme].append(doc_id)

    return index_inverse
   
   
   
   
#3  
   
def intersection(list1, list2):
    i = 0
    j = 0
    result = []

    while i < len(list1) and j < len(list2):

        if list1[i] == list2[j]:
            result.append(list1[i])
            i += 1
            j += 1

        elif list1[i] < list2[j]:
            i += 1

        else:
            j += 1

    return result



#4

def creer_skips(liste):
    n = len(liste)
    inter = max(1, int(math.sqrt(n)))
    skips = {}

    for i in range(0, n, inter):
        position_to_go = i + inter
        if  position_to_go < n:
            skips[i] = position_to_go

    return skips


def intersection_avec_skips(list1, list2):
    i, j = 0, 0
    result = []
    skips1 = creer_skips(list1)
    skips2 = creer_skips(list2)
    while i < len(list1) and j < len(list2):

        if list1[i] == list2[j]:
            result.append(list1[i])
            i += 1
            j += 1

        elif list1[i] < list2[j]:
            if i in skips1 and list1[skips1[i]] <= list2[j]:
                i = skips1[i]
            else:
                i += 1
        else:
            if j in skips2 and list2[skips2[j]] <= list1[i]:
                j = skips2[j]
            else:
                j += 1

    return result

#le test du programme
index_inverse = construire_index(documents)
terme1 = input("Entrez le premier terme a chercher: ")
terme2 = input("Entrez le deuxième terme a chercher : ")
docs1 = index_inverse.get(terme1, [])
docs2 = index_inverse.get(terme2, [])
print(f"Intersection : {intersection(docs1, docs2)}")
print(f"Intersection avec saut: {intersection_avec_skips(docs1, docs2)}")