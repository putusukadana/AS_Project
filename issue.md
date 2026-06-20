# Rencana Implementasi Perbaikan Bug & Refactoring
Dokumen ini berisi panduan langkah-demi-langkah untuk mengimplementasikan perbaikan pada *codebase* AS_Project. Panduan ini dirancang agar dapat dieksekusi dengan mudah oleh *junior programmer* atau *AI assistant*.

Tugas dibagi menjadi dua bagian: **Prioritas Utama** (harus diselesaikan pertama karena menyangkut keamanan dan core bug) dan **Backlog/Peningkatan Lainnya**.

---

## 🔴 PRIORITAS UTAMA (Sprint 1)

### 1. [Keamanan] Fix XSS di `RawSnapshotTable.vue` (CRITICAL)
**Masalah**: Fungsi `openPreview()` menyisipkan data mentah dari komentar TikTok langsung ke HTML string, membuka celah eksekusi *Cross-Site Scripting* (XSS).
**File Tujuan**: `frontend/src/components/.../RawSnapshotTable.vue` (Cari file ini di dalam komponen dashboard/tabel)
**Instruksi Implementasi**:
1. Temukan fungsi `openPreview()`.
2. Buat *helper function* untuk melakukan *escape* HTML sebelum merender:
   ```javascript
   const escapeHTML = (str) => {
     if (!str) return '';
     return str.toString()
       .replace(/&/g, '&amp;')
       .replace(/</g, '&lt;')
       .replace(/>/g, '&gt;')
       .replace(/"/g, '&quot;')
       .replace(/'/g, '&#39;');
   };
   ```
3. Bungkus setiap variabel input (`c.raw_text`, `c.text`, `c.stemmed_text`, `c.user_unique_id`) dengan `escapeHTML()` sebelum disisipkan ke *string template* HTML (`\``).

### 2. [Autentikasi] Tambahkan Interceptor Axios untuk Handle 401 Unauthorized
**Masalah**: Jika token *expired*, API akan mengembalikan 401, tapi frontend tidak otomatis me-logout user dan me-redirect ke halaman login.
**File Tujuan**: `frontend/src/services/api.js` (atau tempat konfigurasi Axios berada)
**Instruksi Implementasi**:
1. Tambahkan *response interceptor* pada *instance* Axios.
2. Cek apakah status error adalah `401`. Jika ya, hapus `token` dan `user` dari `localStorage`, lalu redirect ke halaman login.
   ```javascript
   import router from '@/routes'; // sesuaikan path ke router

   api.interceptors.response.use(
     (response) => response,
     (error) => {
       if (error.response && error.response.status === 401) {
         localStorage.removeItem('token');
         localStorage.removeItem('user');
         // Redirect ke halaman login
         window.location.href = '/login'; 
         // atau router.push('/login') jika memungkinkan
       }
       return Promise.reject(error);
     }
   );
   ```

### 3. [Bug] Hapus Duplikasi Route
**Masalah**: Rute untuk `Dashboard` dan `DataEngine` ditulis dua kali.
**File Tujuan**: `frontend/src/routes/index.js` (atau `router/index.js`)
**Instruksi Implementasi**:
1. Buka file konfigurasi Vue Router.
2. Cari definisi *path* untuk `/dashboard` dan `/data-engine` (atau nama rute yang serupa).
3. Hapus salah satu definisi duplikat tersebut sehingga hanya tersisa satu blok objek untuk setiap *route*.

### 4. [UX] Ganti `alert()` Native dengan Toast Notification
**Masalah**: Validasi file masih menggunakan `alert()` bawaan browser yang mengganggu UX.
**File Tujuan**: `frontend/src/components/.../ExtractionPanel.vue`
**Instruksi Implementasi**:
1. Di bagian `<script setup>`, import `useToast` dari PrimeVue:
   ```javascript
   import { useToast } from 'primevue/usetoast';
   const toast = useToast();
   ```
2. Temukan semua baris kode yang memanggil `alert('pesan error')`.
3. Ganti menjadi:
   ```javascript
   toast.add({ severity: 'error', summary: 'Error', detail: 'pesan error', life: 3000 });
   ```
*(Pastikan komponen `<Toast />` sudah terpasang di layout utama seperti `App.vue`)*.

### 5. [UX] Nonaktifkan Opsi Platform yang Belum Siap
**Masalah**: User bisa memilih Instagram, YouTube, News, dan FB padahal baru TikTok yang berfungsi.
**File Tujuan**: `frontend/src/components/.../ExtractionPanel.vue`
**Instruksi Implementasi**:
1. Cari *array* atau HTML *template* yang mendefinisikan list platform.
2. Tambahkan *property* `disabled: true` (atau *class* CSS khusus seperti `opacity-50 cursor-not-allowed` / *attribute* `disabled` di HTML).
3. Opsional: Tambahkan *tooltip* "Coming Soon" pada platform selain TikTok agar jelas bahwa fitur tersebut masih dikembangkan.

### 6. [Kerapian] Bersihkan Boilerplate & Kode Mati (*Commented-Out*)
**Masalah**: Masih ada sisa *template* bawaan Vite dan blok kode besar yang di-comment out.
**File Tujuan**: Berbagai file di `frontend/src`
**Instruksi Implementasi**:
1. **Hapus file**: `HelloWorld.vue` (jika ada), `assets/vite.svg`, `assets/vue.svg`.
2. **Hapus kode mati**:
   - Di `ResultPanel.vue`: Cari blok `Dataset Summary` yang di-comment out lalu hapus.
   - Di `AppSidebar.vue`: Cari tombol "New Crawl" yang di-comment out lalu hapus.
   - Di `AppTopbar.vue`: Cari bar pencarian (*search bar*) & *last update* yang di-comment out lalu hapus.

### 7. [Arsitektur] Standarisasi Akses Store (Gunakan Pinia Langsung)
**Masalah**: `ObsidianPipeline.vue` menggunakan *props*, sedangkan `DataSummary.vue` dll menggunakan *store* secara langsung.
**File Tujuan**: `frontend/src/components/.../ObsidianPipeline.vue` (dan komponen sejenisnya)
**Instruksi Implementasi**:
1. Hapus *props* yang berhubungan dengan data *crawl* (mis. `pipeline-meta`).
2. Di dalam `<script setup>`, import *store* Pinia:
   ```javascript
   import { useCrawlStore } from '@/stores/crawlStore'; // sesuaikan path
   const crawlStore = useCrawlStore();
   ```
3. Ubah referensi data di *template* untuk langsung membaca dari `crawlStore.namaState` atau *computed property* yang terhubung ke *store*.

---

## 🟡 BACKLOG / PENINGKATAN LAINNYA (Sprint 2)

### 8. Tambahkan Try/Catch pada Parsing `localStorage`
**Masalah**: Parsing data JSON dari localStorage yang *corrupt* dapat membuat aplikasi *crash*.
**File Tujuan**: `frontend/src/components/.../AppTopbar.vue`
**Instruksi Implementasi**:
Bungkus `JSON.parse` dengan `try/catch`.
```javascript
let userData = {};
try {
  const userString = localStorage.getItem('user');
  userData = userString ? JSON.parse(userString) : {};
} catch (error) {
  console.error('Failed to parse user data from localStorage', error);
  localStorage.removeItem('user'); // bersihkan data corrupt
}
```

### 9. Perbaiki Class Tailwind yang Salah
**Masalah**: *Class* warna teks tidak valid.
**File Tujuan**: `frontend/src/views/Login.vue` & `Register.vue`
**Instruksi Implementasi**:
Cari teks `text-white-800`, `text-white-600`, `text-white-500` dan ganti menjadi skala warna abu-abu seperti `text-slate-800`, `text-slate-600`, `text-slate-500` atau `text-gray-*`.

### 10. Matikan Elemen Mockup / Dead UI
**Masalah**: Tombol terlihat bisa diklik tapi tidak berfungsi.
**Instruksi Implementasi**:
- `AIInsightsEngine.vue`: Tambahkan `@click` kosong dengan notifikasi toast "Coming Soon" untuk tombol "📄 PDF Report", atau disable tombolnya.
- `AppTopbar.vue`: Sembunyikan notifikasi 🔔 jika belum ada fungsinya.
- `AppSidebar.vue`: Sembunyikan atau berikan *handler* "Coming Soon" untuk "UPGRADE PLAN".

### 11. Perbaiki *Error Handling*
**Instruksi Implementasi**:
- `auth-service.js`: Ganti `throw error.response?.data?.detail?.message` dengan `throw new Error(...)` agar *stack trace* tetap terjaga.
- `crawlStore.js`: Jangan hanya `console.error` saat `fetchKeywords` gagal. Tangkap error tersebut dan gunakan `toast.add({ severity: 'error', ... })` agar user tahu proses gagal.
- *Mapping* pesan error: Hindari pesan mentah Axios seperti "Network Error", ubah menjadi pesan ramah seperti "Koneksi ke server terputus".

### 12. Refactor `ExtractionPanel.vue` (Pecah Komponen)
**Masalah**: Komponen terlalu gemuk, menangani banyak mode.
**Instruksi Implementasi**:
Ekstrak logika dan *template* menjadi 3 sub-komponen baru: `KeywordForm.vue`, `UrlForm.vue`, dan `UploadForm.vue`. Biarkan `ExtractionPanel.vue` hanya sebagai wadah/induk yang mengatur pergantian *tab* atau *mode*.

### 13. [Tech Debt] Penanganan `EmotionalSpectrum.vue`
**Instruksi Implementasi**: Komponen ini masih memakai data *dummy* dan tidak terhubung ke *store*. Tambahkan komentar `// TODO: Connect to crawlStore when backend API is ready` agar statusnya jelas.

### 14. [Konfigurasi] Tinjau Ulang Dependencies & Tailwind Config
**Masalah**: Versi dependencies terlalu *bleeding edge* dan bercampur aduk antara config v3 dan v4.
**Instruksi Implementasi**:
- Pindahkan `tailwindcss`, `postcss`, dan `autoprefixer` ke bagian `devDependencies` di `package.json`.
- Evaluasi penghapusan `postcss.config.js` dan `tailwind.config.js` jika memang proyek sepenuhnya menggunakan fitur baru Vite plugin untuk Tailwind v4 (`@tailwindcss/vite`).

### 15. Setup Testing (Vitest)
**Instruksi Implementasi**: Install `vitest` dan buat file test pertama, minimal untuk memvalidasi *state machine* / logika di `crawlStore.js` agar mencegah regresi saat ada perubahan fitur *pipeline*.
