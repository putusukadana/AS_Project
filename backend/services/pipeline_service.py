import re
import emoji
import pandas as pd
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from database import db
from models import ProcessedData
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

# --- Inisialisasi Kamus & Stopword ---

# 1. Normalisasi Slang (Alay)
try:
    url_kamus_alay = "https://raw.githubusercontent.com/evrintobing17/NormalisasiKata/master/kamus_alay.csv"
    kamus_df = pd.read_csv(url_kamus_alay, names=['slang', 'normal'], header=None)
    slang_dict = dict(zip(kamus_df['slang'], kamus_df['normal']))
except Exception as e:
    print(f"Peringatan: Gagal memuat kamus alay dari URL. Error: {e}")
    slang_dict = {}

# 2. InSet Sentiment Lexicon
def load_kamus_sentimen(filepath):
    try:
        if not os.path.exists(filepath):
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            filepath = os.path.join(base_dir, filepath.replace("/", "\\"))
            
        df = pd.read_csv(filepath, sep='\t')
        return dict(zip(df['word'].str.lower(), df['weight']))
    except Exception as e:
        print(f"Gagal memuat kamus sentimen: {filepath}. Error: {e}")
        return {}

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path_pos = os.path.join(base_dir, "resources", "InSet", "positive.tsv")
path_neg = os.path.join(base_dir, "resources", "InSet", "negative.tsv")
pos_kamus = load_kamus_sentimen(path_pos)
neg_kamus = load_kamus_sentimen(path_neg)

# 3. Sastrawi Stopword Remover
factory = StopWordRemoverFactory()
stopword_remover = factory.create_stop_word_remover()

# --- Fungsi Pemrosesan ---

def clean_text(teks: str) -> str:
    if not isinstance(teks, str): return ""
    teks = teks.lower()
    teks = re.sub(r'http\S+|www\S+|https\S+', '', teks)
    teks = re.sub(r'#\w+', '', teks)
    teks = re.sub(r'@\w+', '', teks)
    teks = re.sub(r'\W+', ' ', teks)
    teks = re.sub(r'\s+', ' ', teks).strip()
    return teks

def konversi_emoji(teks: str) -> str:
    if not isinstance(teks, str): return ""
    return emoji.demojize(teks, language='id')

def normalisasi_slang(teks: str) -> str:
    if not isinstance(teks, str):
        return ""
    return ' '.join([slang_dict.get(kata, kata) for kata in teks.split()])

def skor_sentimen(teks: str) -> float:
    if not isinstance(teks, str):
        return 0.0
    skor = 0.0
    for kata in teks.lower().split():
        skor += pos_kamus.get(kata, 0)
        skor += neg_kamus.get(kata, 0)
    return skor

def label_sentimen(skor: float) -> str:
    if skor > 0: return 'Positif'
    elif skor < 0: return 'Negatif'
    else: return 'Netral'

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

async def run_emoji_conversion():
    try:
        for video in _current_data:
            if 'comment_sample' in video:
                for comment in video['comment_sample']:
                    if 'text' in comment:
                        comment['text'] = konversi_emoji(comment['text'])
        return {"status": "done", "step": "emoji_conversion", "data": _current_data}
    except Exception as e:
        return {"status": "error", "step": "emoji_conversion", "message": str(e)}

async def run_cleansing():
    try:
        for video in _current_data:
            if 'comment_sample' in video:
                for comment in video['comment_sample']:
                    if 'text' in comment:
                        comment['text'] = clean_text(comment['text'])
        return {"status": "done", "step": "cleansed", "data": _current_data}
    except Exception as e:
        return {"status": "error", "step": "cleansed", "message": str(e)}

async def run_normalization():
    try:
        for video in _current_data:
            if 'comment_sample' in video:
                for comment in video['comment_sample']:
                    if 'text' in comment:
                        comment['text'] = normalisasi_slang(comment['text'])
        return {"status": "done", "step": "normalized", "data": _current_data}
    except Exception as e:
        return {"status": "error", "step": "normalized", "message": str(e)}

async def run_stopwords():
    try:
        for video in _current_data:
            if 'comment_sample' in video:
                for comment in video['comment_sample']:
                    if 'text' in comment:
                        comment['text'] = stopword_remover.remove(comment['text'])
        return {"status": "done", "step": "stopwords", "data": _current_data}
    except Exception as e:
        return {"status": "error", "step": "stopwords", "message": str(e)}

async def run_sentiment_analysis_legacy():
    try:
        processed_items = []
        for video in _current_data:
            if 'comment_sample' in video:
                for comment in video['comment_sample']:
                    if 'text' in comment:
                        score = skor_sentimen(comment['text'])
                        label = label_sentimen(score)
                        comment['score'] = score
                        comment['label'] = label
                        
                        processed_obj = ProcessedData(
                            raw_text=comment.get('raw_text', comment['text']),
                            cleaned_text=comment['text'],
                            score=score,
                            label=label,
                            platform=video.get('platform', 'tiktok'),
                            video_id=video.get('video_id'),
                            author=comment.get('user_unique_id'),
                            created_at=datetime.now()
                        )
                        processed_items.append(processed_obj)
        
        if processed_items:
            await save_processed_data(processed_items)
                
        return {"status": "done", "step": "sentiment", "data": _current_data}
    except Exception as e:
        print(f"Internal Sentiment Error: {e}")
        return {"status": "error", "step": "sentiment", "message": "Terjadi kesalahan pada sistem pemrosesan sentiment analysis."}

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
    res = await run_sentiment_analysis_legacy()
    return res

# Placeholder functions
async def run_case_folding(): return await run_cleansing()
async def run_url_removal(): return await run_cleansing()
async def run_emotion_detection(): return {"status": "done", "step": "emotion", "data": _current_data}
