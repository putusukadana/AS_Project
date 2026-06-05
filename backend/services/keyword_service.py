from collections import Counter

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

    def count_keywords(texts: list) -> list:
        counter = Counter()
        for t in texts:
            words = t.split()
            counter.update(words)
        return [{"text": word, "count": count} for word, count in counter.most_common(top_n)]

    return {
        "status": "done",
        "overall": count_keywords(all_texts),
        "by_label": {
            label: count_keywords(texts)
            for label, texts in texts_by_label.items()
        }
    }
