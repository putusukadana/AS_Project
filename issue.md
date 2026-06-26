# Issue: Integrasi Stopword Tambahan dari File JSON ke Pipeline Stopword Remover

## Deskripsi

Saat ini, fungsi stopword removal di [pipeline_service.py](file:///c:/Users/User/webAS/AS_Project/backend/services/pipeline_service.py) **hanya menggunakan daftar stopword bawaan Sastrawi**. Daftar bawaan ini belum mencakup kata-kata tidak bermakna dari bahasa daerah (Bali), nama tokoh politik, singkatan slang, ekspresi emoji hasil demojize, dan kata-kata umum lainnya yang spesifik untuk konteks penelitian ini.

Sudah tersedia file JSON berisi stopword tambahan di:

```
C:\Users\User\webAS\AS_Project\backend\resources\stopword\stopword_tambahan.json
```

**Tugas ini adalah menggabungkan stopword tambahan dari file JSON tersebut ke dalam proses stopword removal yang sudah ada.**

---

## Konteks Teknis (Wajib Dibaca)

### Kondisi Saat Ini

| Aspek                       | Detail                                                                                                             |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **File yang diubah**        | [pipeline_service.py](file:///c:/Users/User/webAS/AS_Project/backend/services/pipeline_service.py)                 |
| **File sumber data**        | [stopword_tambahan.json](file:///c:/Users/User/webAS/AS_Project/backend/resources/stopword/stopword_tambahan.json) |
| **Library stopword**        | `Sastrawi.StopWordRemover.StopWordRemoverFactory`                                                                  |
| **Fungsi yang terpengaruh** | `run_stopwords()` (line 123-132)                                                                                   |

### Cara Kerja Stopword Saat Ini (Line 22-24)

```python
# 3. Sastrawi Stopword Remover
factory = StopWordRemoverFactory()
stopword_remover = factory.create_stop_word_remover()
```

`StopWordRemoverFactory` membuat stopword remover dengan daftar stopword bawaan Sastrawi saja. Tidak ada stopword kustom yang ditambahkan.

### Struktur File JSON Stopword Tambahan

File `stopword_tambahan.json` berisi objek JSON dengan **9 kategori** sebagai key, dan masing-masing value berupa **array of string**:

```json
{
  "kata_ganti": ["yan", "ane", "cang", ...],
  "kata_sambung_dan_partikel": ["dll", "dst", ...],
  "nama_orang_dan_tokoh_politik": ["koster", "wayan", ...],
  "ekspresi_emoji_dan_kata_tidak_bermakna": ["wajah", "tangan", ...],
  "kata_kerja_umum_tidak_spesifik": ["pakai", "bawa", ...],
  "kata_keterangan_umum": ["ringan", "mestinya", ...],
  "kata_tanya": ["bgamana", "engken", ...],
  "singkatan_akronim_dan_seruan": ["dll", "dst", ...],
  "angka_dan_satuan": ["kilo", "persen", ...],
  "kata_umum_tidak_bermakna": ["orang", "sama", ...],
  "kata_umum_lainnya": ["sama", "beda", ...]
}
```

> [!IMPORTANT]
> Semua value dari **semua kategori** harus digabung menjadi satu `set` flat berisi string. Kategori hanya untuk dokumentasi, tidak perlu dipertahankan saat runtime.

---

## Tahapan Implementasi

### Tahap 1: Tambahkan Import `json` dan `os`

**File:** [pipeline_service.py](file:///c:/Users/User/webAS/AS_Project/backend/services/pipeline_service.py) — **Line 1-2**

Tambahkan import `json` dan `os` di bagian atas file (bersama import lainnya).

```python
import json
import os
```

> [!NOTE]
> `json` dibutuhkan untuk parsing file `.json`. `os` dibutuhkan untuk membangun path yang platform-independent.

---

### Tahap 2: Muat Data Stopword Tambahan dari File JSON

**File:** [pipeline_service.py](file:///c:/Users/User/webAS/AS_Project/backend/services/pipeline_service.py) — Sisipkan **setelah line 21** (setelah blok `except` kamus alay), **sebelum line 22** (sebelum komentar `# 3. Sastrawi Stopword Remover`)

Tambahkan blok kode baru untuk:

1. Menentukan path ke file JSON
2. Membaca dan parse file JSON
3. Menggabungkan semua value dari semua kategori menjadi satu `set`
4. Menangani error jika file tidak ditemukan atau format salah

```python
# 2. Stopword Tambahan dari File JSON
try:
    stopword_json_path = os.path.join(
        os.path.dirname(__file__), '..', 'resources', 'stopword', 'stopword_tambahan.json'
    )
    with open(stopword_json_path, 'r', encoding='utf-8') as f:
        stopword_data = json.load(f)

    # Gabungkan semua kategori menjadi satu set
    stopword_tambahan = set()
    for kategori, kata_list in stopword_data.items():
        if isinstance(kata_list, list):
            for kata in kata_list:
                if isinstance(kata, str) and kata.strip():
                    stopword_tambahan.add(kata.strip().lower())

    print(f"Berhasil memuat {len(stopword_tambahan)} stopword tambahan dari JSON.")
except FileNotFoundError:
    print(f"Peringatan: File stopword tambahan tidak ditemukan di: {stopword_json_path}")
    stopword_tambahan = set()
except json.JSONDecodeError as e:
    print(f"Peringatan: Format JSON stopword tambahan tidak valid. Error: {e}")
    stopword_tambahan = set()
except Exception as e:
    print(f"Peringatan: Gagal memuat stopword tambahan. Error: {e}")
    stopword_tambahan = set()
```

> [!TIP]
> **Mengapa pakai `os.path.join(os.path.dirname(__file__), '..')`?**
> Karena `pipeline_service.py` berada di folder `services/`, kita perlu naik satu level (`..`) untuk ke folder `backend/`, lalu masuk ke `resources/stopword/`. Cara ini lebih aman daripada hardcode absolute path.

> [!WARNING]
> Pastikan path relatif sudah benar. Struktur folder yang diharapkan:
>
> ```
> backend/
> ├── services/
> │   └── pipeline_service.py   ← file ini
> └── resources/
>     └── stopword/
>         └── stopword_tambahan.json   ← file sumber
> ```

---

### Tahap 3: Modifikasi Inisialisasi Sastrawi Stopword Remover

**File:** [pipeline_service.py](file:///c:/Users/User/webAS/AS_Project/backend/services/pipeline_service.py) — **Line 22-24** (blok `# 3. Sastrawi Stopword Remover`)

**Ganti** kode lama:

```python
# 3. Sastrawi Stopword Remover
factory = StopWordRemoverFactory()
stopword_remover = factory.create_stop_word_remover()
```

**Dengan** kode baru yang menggabungkan stopword bawaan Sastrawi + stopword tambahan:

```python
# 3. Sastrawi Stopword Remover (dengan stopword tambahan)
factory = StopWordRemoverFactory()
default_stopwords = set(factory.get_stop_words())      # ambil daftar bawaan Sastrawi (convert list → set)
combined_stopwords = default_stopwords | stopword_tambahan  # gabungkan dengan set tambahan

# Override: buat remover baru dari gabungan stopword
from Sastrawi.StopWordRemover.StopWordRemover import StopWordRemover
from Sastrawi.Dictionary.ArrayDictionary import ArrayDictionary

dictionary = ArrayDictionary(list(combined_stopwords))
stopword_remover = StopWordRemover(dictionary)
```

> [!IMPORTANT]
> **Penjelasan Kunci:**
>
> - `factory.get_stop_words()` mengembalikan **`list`** (bukan `set`), sehingga harus di-wrap dengan `set()` terlebih dahulu
> - Operator `|` menggabungkan dua `set` (union). Alternatif: `default_stopwords.union(stopword_tambahan)`
> - Kita perlu membuat `StopWordRemover` baru secara manual dengan `ArrayDictionary` karena `factory.create_stop_word_remover()` hanya menggunakan daftar bawaan dan tidak menerima parameter tambahan
> - Import `StopWordRemover` dan `ArrayDictionary` dilakukan di sini karena hanya dibutuhkan pada blok ini

---

### Tahap 4: Tidak Ada Perubahan pada Fungsi `run_stopwords()`

**TIDAK PERLU mengubah** fungsi [run_stopwords()](file:///c:/Users/User/webAS/AS_Project/backend/services/pipeline_service.py#L123-L132). Fungsi ini sudah menggunakan variabel `stopword_remover` yang sekarang sudah berisi gabungan stopword bawaan + tambahan.

```python
# Fungsi ini TIDAK PERLU diubah
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
```

> [!NOTE]
> Karena kita hanya mengganti isi variabel `stopword_remover` di level modul (global), semua fungsi yang menggunakan variabel ini otomatis mendapat manfaat dari stopword gabungan tanpa perubahan kode apapun.

---

## Tahap 5: Testing & Verifikasi

### 5.1. Verifikasi Server Bisa Start

```bash
cd C:\Users\User\webAS\AS_Project\backend
py main.py
```

**Yang diharapkan:**

- Server start tanpa error
- Muncul pesan: `Berhasil memuat {N} stopword tambahan dari JSON.` di console
- Tidak ada pesan error/peringatan terkait file JSON

### 5.2. Verifikasi Jumlah Stopword

Tambahkan **sementara** print statement setelah inisialisasi untuk memverifikasi:

```python
print(f"Total stopword bawaan Sastrawi: {len(default_stopwords)}")
print(f"Total stopword tambahan: {len(stopword_tambahan)}")
print(f"Total stopword gabungan: {len(combined_stopwords)}")
```

> [!TIP]
> Hapus print statement ini setelah verifikasi selesai.

### 5.3. Test Fungsional via UI

1. Buka halaman DataEngine di frontend
2. Jalankan pipeline preprocessing sampai tahap **Stopword Removal**
3. Periksa hasil: kata-kata dari stopword tambahan (seperti `"ane"`, `"koster"`, `"wkwk"`, `"moai"`) seharusnya sudah **terhapus** dari teks hasil
4. Bandingkan dengan hasil sebelum perubahan jika memungkinkan

### 5.4. Test Edge Case

| Test Case              | Input                              | Expected Output               |
| ---------------------- | ---------------------------------- | ----------------------------- |
| Kata stopword bawaan   | `"yang dan di ini"`                | `""` (kosong)                 |
| Kata stopword tambahan | `"ane cang koster"`                | `""` (kosong)                 |
| Campuran               | `"ane suka koster membangun bali"` | `"suka membangun"`            |
| Teks kosong            | `""`                               | `""`                          |
| Teks tanpa stopword    | `"pembangunan infrastruktur"`      | `"pembangunan infrastruktur"` |

---

## Ringkasan Perubahan

### File yang Diubah

| File                                                                                               | Aksi       | Deskripsi                                    |
| -------------------------------------------------------------------------------------------------- | ---------- | -------------------------------------------- |
| [pipeline_service.py](file:///c:/Users/User/webAS/AS_Project/backend/services/pipeline_service.py) | **MODIFY** | Tambah import, muat JSON, gabungkan stopword |

### File yang TIDAK Diubah

| File                                                                                                               | Alasan                           |
| ------------------------------------------------------------------------------------------------------------------ | -------------------------------- |
| [stopword_tambahan.json](file:///c:/Users/User/webAS/AS_Project/backend/resources/stopword/stopword_tambahan.json) | Hanya dibaca, tidak dimodifikasi |
| Semua file lain                                                                                                    | Tidak terpengaruh                |

### Kode Final yang Diharapkan (Bagian Atas `pipeline_service.py`)

```python
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
    print(f"Peringatan: File stopword tambahan tidak ditemukan.")
    stopword_tambahan = set()
except json.JSONDecodeError as e:
    print(f"Peringatan: Format JSON stopword tambahan tidak valid. Error: {e}")
    stopword_tambahan = set()
except Exception as e:
    print(f"Peringatan: Gagal memuat stopword tambahan. Error: {e}")
    stopword_tambahan = set()

# 3. Sastrawi Stopword Remover (dengan stopword tambahan)
factory = StopWordRemoverFactory()
default_stopwords = set(factory.get_stop_words())  # list → set
combined_stopwords = default_stopwords | stopword_tambahan

from Sastrawi.StopWordRemover.StopWordRemover import StopWordRemover
from Sastrawi.Dictionary.ArrayDictionary import ArrayDictionary

dictionary = ArrayDictionary(list(combined_stopwords))
stopword_remover = StopWordRemover(dictionary)

# 4. Sastrawi Stemmer
factory_stemmer = StemmerFactory()
stemmer = factory_stemmer.create_stemmer()
```

---

## Checklist Sebelum Merge

- [ ] Import `json` dan `os` ditambahkan
- [ ] File JSON dibaca dengan error handling lengkap
- [ ] Semua kategori digabung menjadi satu `set`
- [ ] Stopword bawaan Sastrawi digabung dengan stopword tambahan
- [ ] `StopWordRemover` dibuat ulang dengan `ArrayDictionary` dari gabungan
- [ ] Server bisa start tanpa error
- [ ] Pesan konfirmasi muncul di console
- [ ] Fungsi `run_stopwords()` tetap berjalan normal
- [ ] Kata-kata dari stopword tambahan berhasil dihapus saat preprocessing
