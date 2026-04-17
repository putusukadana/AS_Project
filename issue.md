# Issue: Implementasi Halaman Dashboard Utama

## Deskripsi Singkat
Membuat halaman **Dashboard** utama aplikasi yang akan menjadi pusat pemantauan analitik sentimen dan emosi dari berbagai platform. Halaman ini memerlukan tata letak kompleks dengan beberapa widget chart, summary stat, dan panel integrasi AI.

## Kebutuhan UI/UX
1. **Sidebar Navigasi & Headbar**: Menggunakan bentuk visual dan tata letak yang konsisten (seperti halaman *DataEngine*). 
   - **Headbar**: Terdapat fitur tambahan yakni: tombol **Download PDF Report**, indikator **Last Update** (di pojok kanan atas), ikon notifikasi (lonceng), dan ikon pengaturan akun/profil.
   - **Sidebar (Kiri Bawah)**: Terdapat keterangan status **Free Version** dan tombol **Upgrade Plan**.
2. **Widget Utama (4 Besar)**:
   - **Sentiment Distribution**: Grafik (Barchart/Stacked) perbandingan sentimen (Positif, Netral, Negatif) antar platform.
   - **Emotional Spectrum**: Grafik (Radar atau Doughnut Chart) distribusi ragam emosi.
   - **Top Keywords**: Daftar kata kunci yang sering muncul, dilengkapi dengan filter *toggle* (Positif/Negatif/Netral).
   - **AI Insights Engine**: Panel teks khusus yang menyajikan analisis otomatis dan rekomendasi tindakan berdasarkan data yang didapat dari AI.
3. **Statistik Ringkas (Bagian Bawah)**:
   - Menampilkan 4 metrik utama: **Global Reach**, **Active Mentions**, **Avg. Sentiment**, dan **Crisis Alerts**.

---

## Tahapan Implementasi (Step-by-Step Guide)

Dokumen ini ditujukan bagi programmer junior atau asisten AI untuk mengimplementasikan halaman tersebut secara sistematis. Prioritaskan penggunaan **Tailwind CSS** untuk styling.

### Tahap 1: Persiapan Struktur Layout & Routing
1. Buat file Vue komponen baru, misalnya di `src/views/Dashboard.vue`.
2. Tambahkan konfigurasi _route_ untuk `/dashboard` di file router Vue Anda.
3. Gunakan atau ekstraksi komponen layout standar (Sidebar dan Headbar) yang sudah ada agar dapat digunakan kembali (reusable).
4. **Modifikasi Sidebar**: Pada bagian paling bawah Sidebar, tambahkan area untuk merender teks keterangan "Free Version" beserta tombol CTA "Upgrade Plan".
5. **Modifikasi Headbar**: Pada seksi kanan Headbar, pasang secara berurutan: Indikator "Last Update: [Waktu]", tombol "Download PDF Report", ikon Lonceng (Notifikasi), dan elemen Profil/Akun.

### Tahap 2: Pembagian Ruang (Grid Layout)
1. Buat struktur grid utama di dalam file `Dashboard.vue` menggunakan kelas Tailwind (misalnya: `grid grid-cols-1 lg:grid-cols-2 gap-6`).
2. Tentukan area (Container) untuk 4 Widget Besar (misal dengan rasio layar yang seimbang) pada bagian atas/tengah.
3. Di luar grid widget besar tersebut, tepatnya di **bagian paling bawah halaman**, siapkan area grid satu baris (misalnya `grid grid-cols-2 lg:grid-cols-4 gap-4`) khusus untuk menampung 4 buah metrik Statistik Ringkas.

### Tahap 3: Implementasi 4 Widget Besar
Gunakan *library* chart bawaan dari *project* (misal: `chart.js` / `apexcharts`). Untuk setiap widget, buat card dengan tampilan modern (gunakan border-radius, background putih/gelap adaptif, shadow tipis).
1. **Widget Sentiment Distribution**:
   - Buat judul: "Sentiment Distribution".
   - Integrasikan *Bar Chart* (Stacked). Sumbu-X berisi list platform, Sumbu-Y berisi jumlah/frekuensi. Gunakan pewarnaan standar: hijau (positif), abu-abu (netral), merah (negatif).
2. **Widget Emotional Spectrum**:
   - Buat judul: "Emotional Spectrum".
   - Integrasikan *Radar Chart* atau *Doughnut Chart* untuk memperlihatkan rasio sebaran emosi.
3. **Widget Top Keywords**:
   - Buat judul: "Top Keywords".
   - Buat 3 opsi tombol tab/filter: Positif, Negatif, Netral.
   - Buat daftar (List) atau Tag Cloud untuk kumpulan *keyword*. Sistem harus bisa menukar *list* yang ditampilkan jika filter di-klik.
4. **Widget AI Insights Engine**:
   - Buat judul: "AI Insights Engine". Berikan aksen visual khusus (misalnya ikon percikan bintang/sparkles atau aksen warna gradasi) untuk membedakannya sebagai fitur "Cerdas".
   - Sediakan ruang paragraf terstruktur untuk merender Insight Point per Point dari analitik AI.

### Tahap 4: Implementasi 4 Statistik Ringkas (Bagian Bawah)
Buat _card_ mini untuk masing-masing angka indikator utama:
1. **Global Reach**: Tampilkan angka total pantauan beserta Ikon Global/Jaringan (Network).
2. **Active Mentions**: Tampilkan angka *mentions* terbaru beserta Ikon Percakapan/Megafon.
3. **Avg. Sentiment**: Tampilkan indikator performa sentimen agregat (misal persentase atau _grade_ nilai) dengan ikon *Smiley* atau kurva naik.
4. **Crisis Alerts**: Tampilkan angka indikator _Alert_ dengan pewarnaan yang menonjolkan fungsi peringatan (misal warna merah bata) dan ikon Danger/Warning.

### Tahap 5: Menyuntikkan Mock Data (State Management dummy)
1. Siapkan semua struktur datanya menggunakan `ref` atau `reactive` (Vue 3 Composition API).
2. Buat data dummy untuk mengisi masing-masing widget (data chart, top keywords beserta ketiganya kategorinya, teks statis untuk AI insights, dan angka dummy untuk stat bottom).
3. Setelah semuanya tampil, tinjau **Responsive Design** agar tampilan tidak rusak walau diakses dari versi perangkat dengan layar sempit (contoh: jadikan grid turun kolom `grid-cols-1` di layar ponsel).
