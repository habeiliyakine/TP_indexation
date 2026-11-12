documents = {}
#Exercice 1
with open("documents.tsv", "r", encoding="utf-8") as fichier:
    for ligne in fichier:
        ligne = ligne.strip()

        if "\t" in ligne:
            doc_id, contenu = ligne.split("\t", 1)
            documents[doc_id] = contenu

print("Nombre de documents :", len(documents))

for doc_id, contenu in documents.items():
    print(doc_id, ":", contenu)
   
# Exercice 2 : Recherche naïve

def recherche_naive(terme, documents):
    resultats = []

    for doc_id, texte in documents.items():
        if terme.lower() in texte.lower():
            resultats.append(doc_id)

    return resultats


terme = input("Entrez un terme :")

print("Résultats :", recherche_naive(terme, documents))


# Exercice 3 : 


import re

# Tokenisation

def tokeniser(texte):
    return re.findall(r"\b\w+\b", texte.lower())


texteatester = documents["D2"]

tokens = tokeniser(texteatester)

print("\nTokens :", tokens)

stopwords = {
    "le", "la", "les", "un", "une",
    "de", "des", "du", "et", "dans",
    "par", "pour", "d", "l"
}


def supprimer_stopwords(tokens):
    resultat = []

    for token in tokens:
        if token not in stopwords:
            resultat.append(token)

    return resultat


tokens_sans_stopwords = supprimer_stopwords(tokens)

print("Tokens après suppression des stopwords :", tokens_sans_stopwords)

# Exercice 4 :

def preprocess(texte):
    tokens = tokeniser(texte)
    tokens = supprimer_stopwords(tokens)
    return tokens

for doc_id, contenu in documents.items():
    termes = preprocess(contenu)
    print(doc_id, ":", termes)
    
#Exercice 5
def construire_index(documents):
    index_inverse = {}

    for doc_id, texte in documents.items():
        termes = preprocess(texte)
        for terme in set(termes):

            # Si le terme n'existe pas encore
            if terme not in index_inverse:
                index_inverse[terme] = []

            # Ajouter le DocID
            index_inverse[terme].append(doc_id)

    # Trier les posting lists
    for terme in index_inverse:
        index_inverse[terme].sort()

    return index_inverse
index = construire_index(documents)

for terme in sorted(index):
    print(terme, "->", index[terme])
#Exercice 6
def rechercher(terme, index_inverse):
 return index_inverse.get(terme.lower(), [])
