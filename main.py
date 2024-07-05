from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import os
from contextlib import asynccontextmanager

from firebase_config import initialize_firebase, download_file_from_firebase
from custom_word_vectors import load_word_vectors, find_similar_words, word_vectors

load_dotenv()

bucket = initialize_firebase()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

@asynccontextmanager
async def lifespan(app: FastAPI):

    await download_file_from_firebase(bucket, 'wiki-news-300d-1M.vec', 'wiki-news-300d-1M.vec')
    await load_word_vectors()
    redis_connection = redis.from_url(REDIS_URL, encoding="utf8")
    await FastAPILimiter.init(redis_connection)
    yield

    await FastAPILimiter.close()

app = FastAPI(lifespan=lifespan)

class WordRequest(BaseModel):
    input: str
    k: int = 10

@app.post("/similar_words/", dependencies=[Depends(RateLimiter(times=1, seconds=60))])
async def get_similar_words(request: WordRequest):
    if word_vectors is None:
        print("Word vectors not loaded yet, loading now...")
        await load_word_vectors()  # Ensure vectors are loaded
    if request.input not in word_vectors:
        raise HTTPException(status_code=404, detail=f"Word '{request.input}' not found in the embeddings")
    print(f"Finding {request.k} similar words for: {request.input}")
    similar_words = find_similar_words(request.input, word_vectors, topn=request.k)
    return {"similar_words": similar_words}

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



# Feel free to use gensim library for loading word vectors. But it creates a following error : 
#         from scipy.linalg import get_blas_funcs, triu
#         ImportError: cannot import name 'triu' from 'scipy.linalg' (C:\Users\91831\Desktop\tes\.venv\Lib\site-packages\scipy\linalg\__init__.py)
# In order to fix this error, I have used custom_word_vectors.py file which creates a custom word vectors using numpy library.

# Using custom_word_vectors.py file increase the time to load similar words. But, it is working fine.
# Using gensim_word_vectors.py file decrease the time to load similar words. But, it creates an error.