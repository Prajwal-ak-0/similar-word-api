import numpy as np
import asyncio

EMBEDDINGS_PATH = 'wiki-news-300d-1M.vec'
word_vectors = None

def load_vectors(fname):
    fin = open(fname, 'r', encoding='utf-8', newline='\n', errors='ignore')
    n, d = map(int, fin.readline().split())
    data = {}
    for line in fin:
        tokens = line.rstrip().split(' ')
        data[tokens[0]] = np.array(tokens[1:], dtype=float)
    return data

async def load_word_vectors():
    global word_vectors
    if word_vectors is None:
        loop = asyncio.get_event_loop()
        print("Loading word vectors...")
        word_vectors = await loop.run_in_executor(None, lambda: load_vectors(EMBEDDINGS_PATH))
        print("Word vectors loaded.")

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def find_similar_words(word, word_vectors, topn=5):
    if word not in word_vectors:
        return []
    word_vector = word_vectors[word]
    similarities = {}
    for w, vec in word_vectors.items():
        if w != word:
            similarities[w] = cosine_similarity(word_vector, vec)
    sorted_similarities = sorted(similarities.items(), key=lambda item: item[1], reverse=True)
    return sorted_similarities[:topn]