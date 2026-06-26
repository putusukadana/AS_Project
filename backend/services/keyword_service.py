from collections import Counter

# Load stopword remover sekali di level modul
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.StopWordRemover.StopWordRemover import StopWordRemover
from Sastrawi.Dictionary.ArrayDictionary import ArrayDictionary
import json, os

_stopword_remover = None

def _get_stopword_remover():
    global _stopword_remover
    if _stopword_remover is not None:
        return _stopword_remover

    factory = StopWordRemoverFactory()
    default_stopwords = set(factory.get_stop_words())

    stopword_tambahan = set()
    json_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'stopword', 'stopword_tambahan.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            for kata_list in json.load(f).values():
                if isinstance(kata_list, list):
                    for kata in kata_list:
                        if isinstance(kata, str) and kata.strip():
                            stopword_tambahan.add(kata.strip().lower())
    except Exception:
        pass

    combined = default_stopwords | stopword_tambahan
    dictionary = ArrayDictionary(list(combined))
    _stopword_remover = StopWordRemover(dictionary)
    return _stopword_remover

async def compute_keywords(top_n: int = 20) -> dict:
    from services.pipeline_service import _current_data

    if not _current_data:
        return {
            "status": "error",
            "message": "Tidak ada data. Jalankan pipeline preprocessing terlebih dahulu.",
            "overall": [],
            "by_label": {}
        }

    texts_by_label = {
        "Positif": [],
        "Netral": [],
        "Negatif": []
    }
    all_texts = []

    for video in _current_data:
        if "comment_sample" not in video or not isinstance(video["comment_sample"], list):
            continue
        for comment in video["comment_sample"]:
            stemmed = comment.get("stemmed_text") or ""
            if not stemmed.strip():
                continue
            all_texts.append(stemmed)
            label = comment.get("sentiment_label", "Netral")
            if label in texts_by_label:
                texts_by_label[label].append(stemmed)

    stopword_remover = _get_stopword_remover()

    def count_keywords(texts: list) -> list:
        counter = Counter()
        for t in texts:
            words = t.split()
            for word in words:
                if stopword_remover.remove(word) == "":
                    continue
                counter.update([word])
        return [{"text": word, "count": count} for word, count in counter.most_common(top_n)]

    return {
        "status": "done",
        "overall": count_keywords(all_texts),
        "by_label": {
            label: count_keywords(texts)
            for label, texts in texts_by_label.items()
        }
    }
