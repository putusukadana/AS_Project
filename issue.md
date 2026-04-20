# Issue: Implementasi Indikator Sisa Kuota API (RapidAPI) di Sidebar

## Deskripsi Singkat
Modifikasi elemen "Storage Status" pada komponen sidebar (`AppSidebar.vue`) menjadi "API Quota Status". Fitur ini bertujuan untuk menampilkan sisa kuota request dari plan RapidAPI yang digunakan (misalnya 93/100 request). Data ini harus diambil secara dinamis dari backend dan ditampilkan dalam bentuk nominal angka serta *progress bar* persentase.

---

## Kebutuhan Fitur (Requirements)
1. **Backend**: Terdapat mekanisme untuk mengetahui dan menyediakan data sisa kuota RapidAPI terakhir ke *frontend* tanpa menghamburkan kuota untuk request tambahan.
2. **Frontend UI**: Elemen statis "Storage Status" di Sidebar diubah menjadi dinamis menampilkan sisa kuota.
3. **Frontend Logic**: Fetch data kuota dari backend saat halaman/sidebar dimuat (atau secara periodik).

---

## Tahapan Implementasi (Step-by-Step Guide)

Dokumen ini ditujukan bagi programmer junior atau asisten AI pendamping untuk mengimplementasikan fitur status kuota secara terstruktur.

### Tahap 1: Persiapan Backend (Menyimpan Status Kuota Terakhir)
Karena memanggil API RapidAPI hanya untuk mengecek kuota akan membuang kuota yang berharga, gunakan pendekatan _caching_ pasif:
1. Buka file service yang mengatur request ke RapidAPI, seperti `backend/services/crawl_tiktok_service.py`.
2. Buat variabel global atau *in-memory cache* (misalnya `last_api_quota = {"remaining": 0, "limit": 100}`).
3. Pada fungsi `safe_api_request`, cari bagian kode yang mengambil nilai dari _headers_ respons:
   ```python
   rem = response.headers.get('x-ratelimit-requests-remaining')
   lim = response.headers.get('x-ratelimit-requests-limit')
   ```
4. Tambahkan logika untuk memperbarui variabel `last_api_quota` dengan nilai integer dari `rem` dan `lim` setiap kali request berhasil. Jika nilai tidak ada (karena API gagal atau belum pernah request awal), bisa di-set ke _default value_.

### Tahap 2: Bikin Endpoint API di Backend
1. Buka file router/controller utama (misalnya `backend/main.py` atau file khusus API monitoring).
2. Tambahkan endpoint baru dengan format: `GET /api/v1/quota`.
3. Kembalikan nilai JSON berisi variabel kuota yang sudah disimpan pada Tahap 1.
   *Contoh Response:*
   ```json
   {
     "status": "success",
     "data": {
       "remaining": 93,
       "limit": 100
     }
   }
   ```

### Tahap 3: Persiapan Frontend (Store / API Fetch)
1. Buka file yang mengatur panggilan API ke backend di Frontend (misalnya `frontend/src/api/` atau langsung di komponen).
2. Di dalam komponen `frontend/src/components/layout/AppSidebar.vue`, siapkan state menggunakan `ref` dari Vue 3 Composition API:
   ```vue
   const quotaRemaining = ref(0);
   const quotaLimit = ref(100);
   const quotaPercentage = computed(() => {
     if (quotaLimit.value === 0) return 0;
     return Math.round((quotaRemaining.value / quotaLimit.value) * 100);
   });
   ```
3. Buat fungsi `fetchQuotaStatus()` menggunakan `fetch` atau `axios` untuk memanggil endpoint `GET /api/v1/quota` yang dibuat pada Tahap 2.
4. Panggil fungsi `fetchQuotaStatus()` di dalam _hook_ `onMounted(() => { ... })`.

### Tahap 4: Modifikasi UI `AppSidebar.vue`
Temukan blok kode HTML berikut di dalam template `AppSidebar.vue`:
```html
<div class="flex items-center gap-2 mb-2">
  <span class="text-xs font-bold text-slate-400 uppercase tracking-widest">Storage Status</span>
  <span class="ml-auto text-xs font-bold text-indigo-600">85%</span>
</div>
<div class="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden">
  <div class="bg-indigo-500 h-full w-[85%] group-hover:bg-indigo-600 transition-colors"></div>
</div>
```

**Ubah menjadi:**
1. Ganti teks "Storage Status" menjadi **"API Quota"** atau **"Requests Left"**.
2. Ganti angka persentase statis `"85%"` dengan variabel teks yang menunjukkan nominal yang tersisa dan *limit*nya, misalnya: `{{ quotaRemaining }} / {{ quotaLimit }}`.
3. Ubah logika *progress bar* agar lebar elemen bereaksi terhadap persen kuota secara dinamis:
   ```html
   <div 
     class="bg-indigo-500 h-full group-hover:bg-indigo-600 transition-all duration-500"
     :style="{ width: quotaPercentage + '%' }"
   ></div>
   ```
   *(Opsional: Berikan warna khusus seperti `bg-red-500` jika indikator `quotaPercentage` berada di bawah 10% untuk indikasi bahaya).*

### Tahap 5: Testing & Validasi
1. Pastikan tidak ada _error_ saat memuat Dashboard, meskipun backend belum pernah melakukan request crawling.
2. Lakukan satu _crawling_ singkat.
3. Refresh atau panggil ulang data di Frontend, pastikan angka sisa kuota (misalnya turun dari 94 ke 93) ter-update dengan benar pada indikator sidebar.
