import re
import json
import os
import emoji
import pandas as pd

from datetime import datetime
from typing import List, Dict, Any, Optional
from database import db
from models import ProcessedData
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# --- Inisialisasi Kamus & Stopword ---

# 1. Normalisasi Slang (Alay)
try:
    url_kamus_alay = "https://raw.githubusercontent.com/evrintobing17/NormalisasiKata/master/kamus_alay.csv"
    kamus_df = pd.read_csv(url_kamus_alay, names=['slang', 'normal'], header=None)
    slang_dict = dict(zip(kamus_df['slang'], kamus_df['normal']))
except Exception as e:
    print(f"Peringatan: Gagal memuat kamus alay dari URL. Error: {e}")
    slang_dict = {}

# 2. Stopword Tambahan dari File JSON
try:
    stopword_json_path = os.path.join(
        os.path.dirname(__file__), '..', 'resources', 'stopword', 'stopword_tambahan.json'
    )
    with open(stopword_json_path, 'r', encoding='utf-8') as f:
        stopword_data = json.load(f)

    stopword_tambahan = set()
    for kategori, kata_list in stopword_data.items():
        if isinstance(kata_list, list):
            for kata in kata_list:
                if isinstance(kata, str) and kata.strip():
                    stopword_tambahan.add(kata.strip().lower())

    print(f"Berhasil memuat {len(stopword_tambahan)} stopword tambahan dari JSON.")
except FileNotFoundError:
    print("Peringatan: File stopword tambahan tidak ditemukan.")
    stopword_tambahan = set()
except json.JSONDecodeError as e:
    print(f"Peringatan: Format JSON stopword tambahan tidak valid. Error: {e}")
    stopword_tambahan = set()
except Exception as e:
    print(f"Peringatan: Gagal memuat stopword tambahan. Error: {e}")
    stopword_tambahan = set()

# 3. Sastrawi Stopword Remover (dengan stopword tambahan)
factory = StopWordRemoverFactory()
default_stopwords = set(factory.get_stop_words())
combined_stopwords = default_stopwords | stopword_tambahan

from Sastrawi.StopWordRemover.StopWordRemover import StopWordRemover
from Sastrawi.Dictionary.ArrayDictionary import ArrayDictionary

dictionary = ArrayDictionary(list(combined_stopwords))
stopword_remover = StopWordRemover(dictionary)

# 4. Sastrawi Stemmer
factory_stemmer = StemmerFactory()
stemmer = factory_stemmer.create_stemmer()

# --- Fungsi Pemrosesan ---

def clean_text(teks: str) -> str:
    if not isinstance(teks, str): return ""
    teks = teks.lower()
    teks = re.sub(r'http\S+|www\S+|https\S+', '', teks)
    teks = re.sub(r'#\w+', '', teks)
    teks = re.sub(r'@\w+', '', teks)
    teks = re.sub(r'\W+', ' ', teks)
    teks = re.sub(r'\b\d+\b', '', teks)
    teks = re.sub(r'\s+', ' ', teks).strip()
    return teks

def konversi_emoji(teks: str) -> str:
    if not isinstance(teks, str): return ""
    return emoji.demojize(teks, language='id')

def normalisasi_slang(teks: str) -> str:
    if not isinstance(teks, str):
        return ""
    return ' '.join([slang_dict.get(kata, kata) for kata in teks.split()])

def stem_text(teks: str) -> str:
    if not isinstance(teks, str):
        return ""
    return stemmer.stem(teks)

async def save_processed_data(data: List[ProcessedData]):
    if not data: return
    collection = db["processed_results"]
    documents = [d.model_dump() for d in data]
    result = await collection.insert_many(documents)
    return len(result.inserted_ids)

# --- Legacy/Backward Compatibility Functions (Modified for comment_sample) ---

_current_data = []

def set_current_data(data):
    try:
        global _current_data
        # Inisialisasi raw_text untuk perbandingan di preview
        for video in data:
            if 'comment_sample' in video and isinstance(video['comment_sample'], list):
                for comment in video['comment_sample']:
                    if 'raw_text' not in comment:
                        comment['raw_text'] = comment.get('text', '')
        _current_data = data
    except Exception as e:
        print(f"Error initializing data: {e}")
        _current_data = []

def _pipeline_meta():
    total_videos = len(_current_data)
    total_comments = sum(
        len(v.get("comment_sample", []))
        for v in _current_data
        if "comment_sample" in v
    )
    return {"total_videos": total_videos, "total_comments": total_comments}

async def run_emoji_conversion():
    try:
        for video in _current_data:
            if 'comment_sample' in video:
                for comment in video['comment_sample']:
                    if 'text' in comment:
                        comment['text'] = konversi_emoji(comment['text'])
        return {"status": "done", "step": "emoji_conversion", "data": _current_data, "meta": _pipeline_meta()}
    except Exception as e:
        return {"status": "error", "step": "emoji_conversion", "message": str(e)}

async def run_cleansing():
    try:
        for video in _current_data:
            if 'comment_sample' in video:
                for comment in video['comment_sample']:
                    if 'text' in comment:
                        comment['text'] = clean_text(comment['text'])
        return {"status": "done", "step": "cleansed", "data": _current_data, "meta": _pipeline_meta()}
    except Exception as e:
        return {"status": "error", "step": "cleansed", "message": str(e)}

async def run_normalization():
    try:
        for video in _current_data:
            if 'comment_sample' in video:
                for comment in video['comment_sample']:
                    if 'text' in comment:
                        comment['text'] = normalisasi_slang(comment['text'])
        return {"status": "done", "step": "normalized", "data": _current_data, "meta": _pipeline_meta()}
    except Exception as e:
        return {"status": "error", "step": "normalized", "message": str(e)}

async def run_stopwords():
    try:
        for video in _current_data:
            if 'comment_sample' in video:
                for comment in video['comment_sample']:
                    if 'text' in comment:
                        comment['text'] = stopword_remover.remove(comment['text'])
        return {"status": "done", "step": "stopwords", "data": _current_data, "meta": _pipeline_meta()}
    except Exception as e:
        return {"status": "error", "step": "stopwords", "message": str(e)}

async def run_stemming():
    try:
        processed_items = []
        total_skipped = 0
        for video in _current_data:
            if 'comment_sample' in video:
                for comment in video['comment_sample'][:]:
                    if 'text' in comment:
                        stemmed = stem_text(comment['text'])
                        comment['stemmed_text'] = stemmed
                        
                        # Skip jika stemmed kosong
                        if not stemmed or stemmed.strip() == "":
                            video["comment_sample"].remove(comment)
                            total_skipped += 1
                            continue
                        
                        processed_obj = ProcessedData(
                            raw_text=comment.get('raw_text') or comment.get('text') or "",
                            cleaned_text=comment.get('text') or "",
                            stemmed_text=stemmed,
                            platform=video.get('platform') or 'tiktok',
                            video_id=video.get('video_id') or "",
                            author=comment.get('user_unique_id') or "Unknown",
                            created_at=datetime.now()
                        )
                        processed_items.append(processed_obj)
        
        meta = _pipeline_meta()
        meta["total_filtered"] = total_skipped
        
        if processed_items:
            await save_processed_data(processed_items)
                
        return {"status": "done", "step": "stemming", "data": _current_data, "meta": meta}
    except Exception as e:
        print(f"Internal Stemming Error: {e}")
        return {"status": "error", "step": "stemming", "message": "Terjadi kesalahan pada sistem pemrosesan stemming."}

# Orchestrator (Optional, for batch processing from scratch)
async def execute_pipeline(raw_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    # This function is not currently used by the UI route-by-route flow, 
    # but kept for potential future batch use. 
    # Logic should be updated similarly if used.
    set_current_data(raw_data_list)
    await run_emoji_conversion()
    await run_cleansing()
    await run_normalization()
    await run_stopwords()
    res = await run_stemming()
    return res

# Placeholder functions
async def run_case_folding(): return await run_cleansing()
async def run_url_removal(): return await run_cleansing()
async def run_emotion_detection(): return {"status": "done", "step": "emotion", "data": _current_data}
