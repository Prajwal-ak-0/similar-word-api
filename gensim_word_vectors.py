from gensim.models import KeyedVectors
import asyncio

EMBEDDINGS_PATH = 'wiki-news-300d-1M.vec'
word_vectors = None

async def load_word_vectors():
    global word_vectors
    if word_vectors is None:
        loop = asyncio.get_event_loop()
        print("Loading word vectors using gensim...")
        word_vectors = await loop.run_in_executor(None, lambda: KeyedVectors.load_word2vec_format(EMBEDDINGS_PATH, binary=False))
        print("Word vectors loaded.")

def find_similar_words(word, topn=5):
    if word not in word_vectors:
        return []
    similar_words = word_vectors.similar_by_word(word, topn=topn)
    return similar_words