import functools

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@functools.lru_cache(maxsize=1)
def load_sentence_model():
    try:
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer("all-MiniLM-L6-v2")
    except Exception:
        return None


def encode_texts(texts):
    model = load_sentence_model()
    texts = [text or "" for text in texts]
    if model is not None:
        return model.encode(texts, normalize_embeddings=True)
    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        return vectorizer.fit_transform(texts).toarray()
    except ValueError:
        return np.zeros((len(texts), 1))


def semantic_similarity(text_a, text_b):
    embeddings = encode_texts([text_a, text_b])
    if embeddings.shape[0] < 2:
        return 0.0
    return float(cosine_similarity([embeddings[0]], [embeddings[1]])[0][0])


@functools.lru_cache(maxsize=1)
def cached_skill_embeddings():
    from nlp.skills_db import ALL_SKILLS

    return encode_texts(tuple(ALL_SKILLS))

