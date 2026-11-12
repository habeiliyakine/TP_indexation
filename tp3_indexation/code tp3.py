import re
from collections import Counter
import math
documents = { }

stopwords = {
"le", "la", "les", "un", "une",
"de", "des", "du", "et", "dans",
"par", "pour", "d", "l"
}
#on choisit des documents proches thematiquement pour mieux evaluer la difference de classement 
with open("documents.tsv", "r", encoding="utf-8") as fichier:
    for ligne in fichier:
        doc_id, contenu = ligne.strip().split("\t", 1)
        documents[doc_id] = contenu

for doc_id, contenu in documents.items():
    print(doc_id, "", contenu)
#on applique exactement le meme pipeline de pretraitement aux documents et aux requetes pour que la recherche soit coherante et eviter la construction des representations incoherantes  
def pretraitement(texte, stemming=False):

    texte = texte.lower()
    tokens = re.findall(r"\b\w+\b", texte)
    tokens = [t for t in tokens if t not in stopwords]
    if stemming:
        tokens = [normaliser_mot(t) for t in tokens]
    return tokens

def construire_index_enrichi(documents, stemming=False):
    index_inverse = {}
    for doc_id, contenu in documents.items():
        tokens = pretraitement(contenu,stemming)
        frequences = Counter(tokens)
        for terme, tf in frequences.items():
            if terme not in index_inverse:
                index_inverse[terme] = {
                    "df": 0,
                    "postings": {}
                }
            index_inverse[terme]["df"] += 1

            index_inverse[terme]["postings"][doc_id] = {
                "tf": tf
            }
    return index_inverse
#notre index inverse est pret
index_inverse = construire_index_enrichi(documents)
#comment calculer idf ?
def calculer_idf(terme, index_inverse, N):
    df = index_inverse[terme]["df"]
    idf = math.log10(N / df)
    return idf

# calculer l'idf de chaque terme 
N = len(documents)

for terme, infos in index_inverse.items():
    df = infos["df"]
    idf = calculer_idf(terme, index_inverse, N)
    print(terme, "DF =", df, "IDF =", round(idf, 3))
#identifier le df de terme maximal    
terme_max_df = max(
    index_inverse,
    key=lambda t: index_inverse[t]["df"]
)

#identifier le df de terme maximal    
terme_min_df = min(
    index_inverse,
    key=lambda t: index_inverse[t]["df"]
)
#identifier le terme avec le plus grand idf : puisque un terme a un petit df  cad plus rare alors il a un idf plus eleve    
terme_max_idf = max(
    index_inverse,
    key=lambda t: calculer_idf(t, index_inverse, N)
)

print("DF maximal :", terme_max_df)
print("DF minimal :", terme_min_df)
print("IDF maximal :", terme_max_idf)


#verifier si le terme existe dans l'index et calculer son poids alors
def poids_tfidf(terme, doc_id, index_inverse, N):

    if terme not in index_inverse:
        return 0
    postings = index_inverse[terme]["postings"]
    if doc_id not in postings:
        return 0
    
    tf = postings[doc_id]["tf"]
    idf = calculer_idf(terme, index_inverse, N)
    poids = (1 + math.log10(tf)) * idf

    return poids

#afficher les identifiants des doculments pour savoir quoi ecrire 
print("Identifiants disponibles :", list(documents.keys()))
#afficher le poids pour un document
doc_id = input("donner l'id de document que tu veux calculer son poids") 

resultats = []

for terme in index_inverse:

    poids = poids_tfidf(terme, doc_id, index_inverse, N)
    if poids > 0:
        tf = index_inverse[terme]["postings"][doc_id]["tf"]
        df = index_inverse[terme]["df"]
        idf = calculer_idf(terme, index_inverse, N)
        resultats.append((terme, tf, df, idf, poids))
resultats.sort(key=lambda x: x[4], reverse=True)

print("TERM    TF   DF   IDF   TF-IDF")

for terme, tf, df, idf, poids in resultats:
    print(terme, tf, df, round(idf, 3), round(poids, 3))



#construire le vocabulaire
vocabulary = sorted(index_inverse.keys())
print("Taille du vocabulaire :", len(vocabulary))
print(vocabulary)

#parcourt le vocabulaire et calcule le poids de chaque terme dans le document 
def document_vector(doc_id, vocabulary, index_inverse, N):
    vector = []
    for terme in vocabulary:
        poids = poids_tfidf(
            terme, doc_id, index_inverse, N
        )
        vector.append(poids)
    return vector
#on effectue le proccesus vectoriel pour les 3 premiers documents
for doc_id in ["doc1:", "doc2:", "doc3:"]:

    vector = document_vector(
        doc_id, vocabulary, index_inverse, N
    )

    nb_zero = vector.count(0)

    print(doc_id, ":", vector)

    print("Nombre de composantes nulles :", nb_zero)
#les documents sont creux car ils contiennent un petit nombre des terme par rapport celui de vocabulaire global
#constuire une requete et la preparer pour la recherche
def query_vector(query, vocabulary, index_inverse, N,stemming=False):

    tokens = pretraitement(query,stemming)
    frequences = Counter(tokens)
    vector_q = []

    for terme in vocabulary:

        if terme in frequences and terme in index_inverse:
            tf = frequences[terme]
            idf = calculer_idf(terme, index_inverse, N)
            poids = (1 + math.log10(tf)) * idf
        else:
            poids = 0

        vector_q.append(poids)
    return vector_q
#on faire un teste de cette fonction 
q = "information retrieval model"

vector_q = query_vector(q, vocabulary, index_inverse, N)
print("Vecteur de la requête :", vector_q)
print("Termes non nuls :")
for i, terme in enumerate(vocabulary):
    if vector_q[i] != 0:
        print(terme, ":", round(vector_q[i], 3))
#si on ne trouve pas le terme dans le tf donc on lignore poids=0

#calculer a similariter en utilisant le cosinus
def cosine_similarity(v1, v2):
    # Calcul du produit scalaire
    produit_scalaire = 0
    for i in range(len(v1)):
        produit_scalaire += v1[i] * v2[i]

    # Calcul de la norme de v1
    norme1 = math.sqrt(sum(x**2 for x in v1))

    # Calcul de la norme de v2
    norme2 = math.sqrt(sum(x**2 for x in v2))

    # Eviter la division par zero
    if (norme1 == 0 or norme2 == 0):
        return 0

    # Calcul de la similarite
    score = produit_scalaire / (norme1 * norme2)
    return score
#calculer la similarite avec tous les documents
for doc_id in documents:
    vector_d = document_vector(
        doc_id, vocabulary, index_inverse, N
    )
    score = cosine_similarity(vector_q, vector_d)
    print(doc_id, ":", round(score, 4))
#la valeur de la similarite est entre 0 et 1 => plus grande plus similaire
def search(query, documents, index_inverse, vocabulary, N, k=5,stemming=False):

    # construire le vecteur de la requête
    vector_q = query_vector(
        query, vocabulary, index_inverse, N
    )

    resultats = []
    for doc_id in documents:

        # Construire le vecteur du document
        vector_d = document_vector(
            doc_id, vocabulary, index_inverse, N
        )

        # Calculer la similarite
        score = cosine_similarity(vector_q, vector_d)

        # Eliminer les scores nuls
        if score > 0:

            resultats.append((doc_id, score))

    # Trier par score decroissant
    resultats.sort(key=lambda x: x[1], reverse=True)

    # Retourner les k premiers
    return resultats[:k]
# on va faire le test du classement essayons 5 requetes 
requetes = [
    "information retrieval model",
    "vector space model",
    "boolean retrieval operators",
    "TF IDF document ranking",
    "neural embeddings dense retrieval"
]

for q in requetes:

    print("\nQUERY :", q)

    resultats = search(
        q, documents, index_inverse, vocabulary, N, k=5
    )

    print("TOP 5 RESULTS")
    for rang, (doc_id, score) in enumerate(resultats, start=1):
        print(
            rang,
            doc_id,
            round(score, 4),
            documents[doc_id]
        )
        
#Exercice10
def normaliser_mot(mot):

    if mot == "documents":
        return "document"

    return mot
# sans normalistaion pas de stemming
index_A = construire_index_enrichi(documents, stemming=False)

vocab_A = sorted(index_A.keys())

resultats_A = search(
    "information retrieval document",
    documents,
    index_A,
    vocab_A,
    N,
    k=10,
    stemming=False
)

print("SANS NORMALISATION")

for rang, (doc_id, score) in enumerate(resultats_A, start=1):

    print(rang, doc_id, round(score, 4))
    
# avec normalisation
index_B = construire_index_enrichi(documents, stemming=True)

vocab_B = sorted(index_B.keys())

resultats_B = search(
    "information retrieval document",
    documents,
    index_B,
    vocab_B,
    N,
    k=10,
    stemming=True
)

print("AVEC NORMALISATION")

for rang, (doc_id, score) in enumerate(resultats_B, start=1):

    print(rang, doc_id, round(score, 4))
    
