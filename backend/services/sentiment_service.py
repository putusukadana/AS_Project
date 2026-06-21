import os
import warnings

try:
    import torch
    from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
    _TORCH_AVAILABLE = True
except ImportError:
    torch = None
    DistilBertTokenizer = None
    DistilBertForSequenceClassification = None
    _TORCH_AVAILABLE = False
    warnings.warn("torch/transformers not installed. Sentiment analysis will be unavailable.")

from database import db

# =====================================================================
# KONSTANTA
# =====================================================================
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ml_model")

# Mapping label index ke nama label yang mudah dibaca
LABEL_MAP = {
    0: "Negatif",
    1: "Netral",
    2: "Positif"
}

# =====================================================================
# INISIALISASI MODEL (hanya dilakukan sekali saat server pertama jalan)
# =====================================================================
tokenizer = None
model = None
if _TORCH_AVAILABLE:
    print(f"[Sentiment] Memuat model dari {MODEL_DIR}...")
    tokenizer = DistilBertTokenizer.from_pretrained(MODEL_DIR)
    model = DistilBertForSequenceClassification.from_pretrained(MODEL_DIR)
    model.eval()  # Set ke mode evaluasi (tidak ada gradient update)
    print("[Sentiment] Model berhasil dimuat.")
else:
    print("[Sentiment] torch/transformers tidak tersedia. Skipping model load.")


# =====================================================================
# FUNGSI UTAMA
# =====================================================================

def predict_sentiment(text: str) -> dict:
    if not _TORCH_AVAILABLE or model is None:
        return {"label": "Netral", "score": 0.0, "label_index": 1, "error": "Model not loaded"}

    if not text or not isinstance(text, str) or text.strip() == "":
        return {"label": "Netral", "score": 0.0, "label_index": 1}

    # Tokenisasi
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=512,
        padding=True
    )

    # Inferensi (tanpa menghitung gradient untuk hemat memori)
    with torch.no_grad():
        outputs = model(**inputs)

    # Ambil probabilitas menggunakan softmax
    probabilities = torch.softmax(outputs.logits, dim=-1)
    predicted_index = torch.argmax(probabilities, dim=-1).item()
    confidence_score = probabilities[0][predicted_index].item()

    return {
        "label": LABEL_MAP[predicted_index],
        "score": round(confidence_score, 4),
        "label_index": predicted_index
    }


async def run_sentiment_analysis() -> dict:
    """
    Menjalankan prediksi sentimen pada SEMUA komentar dalam _current_data
    (data global hasil pipeline dari pipeline_service.py).

    Mengembalikan hasil analisis lengkap beserta ringkasan statistik.
    """
    if not _TORCH_AVAILABLE or model is None:
        return {
            "status": "error",
            "message": "Sentiment analysis tidak tersedia. torch/transformers tidak terinstall.",
            "data": [],
            "summary": {}
        }

    from services.pipeline_service import _current_data  # Import di sini agar selalu ambil versi terbaru

    if not _current_data:
        return {
            "status": "error",
            "message": "Tidak ada data. Jalankan pipeline preprocessing terlebih dahulu.",
            "data": [],
            "summary": {}
        }

    total_comments = 0
    sentiment_counts = {"Positif": 0, "Netral": 0, "Negatif": 0}
    collection = db["processed_results"]

    # Loop setiap video
    for video in _current_data:
        if "comment_sample" not in video or not isinstance(video["comment_sample"], list):
            continue

        # Loop setiap komentar dalam video
        for comment in video["comment_sample"]:
            # Gunakan stemmed_text jika ada, fallback ke text
            text_to_analyze = comment.get("stemmed_text") or comment.get("text") or ""

            result = predict_sentiment(text_to_analyze)

            # Tambahkan hasil prediksi langsung ke object komentar
            comment["sentiment_label"] = result["label"]
            comment["sentiment_score"] = result["score"]

            # Akumulasi statistik
            sentiment_counts[result["label"]] += 1
            total_comments += 1

            # Update ke MongoDB
            await collection.update_many(
                {
                    "raw_text": comment.get("raw_text") or comment.get("text") or "",
                    "video_id": video.get("video_id") or ""
                },
                {
                    "$set": {
                        "sentiment_label": result["label"],
                        "sentiment_score": result["score"]
                    }
                }
            )

    # Hitung persentase
    summary = {}
    if total_comments > 0:
        summary = {
            "total_comments": total_comments,
            "positif": sentiment_counts["Positif"],
            "netral": sentiment_counts["Netral"],
            "negatif": sentiment_counts["Negatif"],
            "pct_positif": round(sentiment_counts["Positif"] / total_comments * 100, 1),
            "pct_netral": round(sentiment_counts["Netral"] / total_comments * 100, 1),
            "pct_negatif": round(sentiment_counts["Negatif"] / total_comments * 100, 1),
        }

    return {
        "status": "done",
        "message": f"Analisis selesai. {total_comments} komentar dianalisis.",
        "data": _current_data,   # Data dengan field sentiment_label & sentiment_score sudah ditambahkan
        "summary": summary
    }
