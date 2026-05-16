from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_text_similarity(text1, text2):
    """Return lightweight TF-IDF cosine similarity between two texts."""
    text1 = (text1 or "").strip()
    text2 = (text2 or "").strip()
    if not text1 or not text2:
        return 0.0

    try:
        vectors = TfidfVectorizer(stop_words="english", ngram_range=(1, 2)).fit_transform([text1, text2])
        score = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        return float(max(0.0, min(1.0, score)))
    except ValueError:
        return 0.0
