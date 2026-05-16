import functools
import re


@functools.lru_cache(maxsize=1)
def load_spacy_model():
    try:
        import spacy

        return spacy.load("en_core_web_sm")
    except Exception:
        return None


def process_text(text):
    nlp = load_spacy_model()
    if nlp is None:
        sentences = re.split(r"(?<=[.!?])\s+", text or "")
        return None, [sentence.strip() for sentence in sentences if sentence.strip()], []
    doc = nlp(text or "")
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return doc, sentences, entities

