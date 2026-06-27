import csv
import json
import io
import time
from typing import List, Dict, Any, Optional

import pandas as pd

TEXT_COLUMN_CANDIDATES = [
    "text", "comment", "komentar", "content", "review",
    "message", "pesan", "caption", "isi", "teks",
    "comment_text", "review_text", "body"
]

AUTHOR_COLUMN_CANDIDATES = [
    "username", "user", "author", "nama", "name",
    "user_unique_id", "commenter", "reviewer", "pengguna"
]


def _detect_column(columns: List[str], candidates: List[str]) -> Optional[str]:
    col_lower_map = {c.lower().strip(): c for c in columns}
    for candidate in candidates:
        if candidate in col_lower_map:
            return col_lower_map[candidate]
    return None


def _parse_csv(file_bytes: bytes) -> List[Dict[str, Any]]:
    text = file_bytes.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    return [row for row in reader]


def _parse_json(file_bytes: bytes) -> List[Dict[str, Any]]:
    text = file_bytes.decode("utf-8-sig")
    data = json.loads(text)
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                return value
        return [data]
    return []


def _parse_excel(file_bytes: bytes) -> List[Dict[str, Any]]:
    df = pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")
    df = df.dropna(how="all")
    df = df.fillna("")
    return df.to_dict(orient="records")


def parse_uploaded_file(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    try:
        if ext == "csv":
            rows = _parse_csv(file_bytes)
        elif ext == "json":
            rows = _parse_json(file_bytes)
        elif ext in ("xlsx", "xls"):
            rows = _parse_excel(file_bytes)
        else:
            return {
                "status": "error",
                "message": f"Format file '.{ext}' tidak didukung. Gunakan .csv, .json, atau .xlsx",
                "total": 0,
                "signal_quality": 0,
                "data": []
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Gagal membaca file: {str(e)}",
            "total": 0,
            "signal_quality": 0,
            "data": []
        }

    if not rows:
        return {
            "status": "error",
            "message": "File kosong atau tidak berisi data yang valid.",
            "total": 0,
            "signal_quality": 0,
            "data": []
        }

    columns = list(rows[0].keys())
    text_col = _detect_column(columns, TEXT_COLUMN_CANDIDATES)
    author_col = _detect_column(columns, AUTHOR_COLUMN_CANDIDATES)

    if not text_col:
        text_col = columns[0]

    comment_sample = []
    for row in rows:
        teks = str(row.get(text_col, "")).strip()
        if not teks:
            continue
        comment = {
            "text": teks,
            "raw_text": teks,
            "user_unique_id": str(row.get(author_col, "Unknown")).strip() if author_col else "Unknown"
        }
        comment_sample.append(comment)

    if not comment_sample:
        return {
            "status": "error",
            "message": f"Tidak ditemukan data teks yang valid di kolom '{text_col}'.",
            "total": 0,
            "signal_quality": 0,
            "data": []
        }

    virtual_video = {
        "video_id": f"upload_{int(time.time())}",
        "platform": "upload",
        "description": f"Data upload dari file: {filename}",
        "comment_count": len(comment_sample),
        "estimated_size_kb": round(len(comment_sample) * 0.15, 2),
        "comment_sample": comment_sample
    }

    return {
        "status": "success",
        "message": f"Berhasil memproses {len(comment_sample)} baris data dari '{filename}' (kolom teks: '{text_col}')",
        "total": len(comment_sample),
        "signal_quality": 95,
        "data": [virtual_video]
    }
