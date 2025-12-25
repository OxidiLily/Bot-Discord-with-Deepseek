# 🤖 Bot Discord with DeepSeek

Proyek ini adalah bot Discord cerdas yang mengintegrasikan kemampuan AI dari **DeepSeek** untuk percakapan natural dan menyediakan informasi cuaca akurat dari **BMKG** (Badan Meteorologi, Klimatologi, dan Geofisika).

Bot ini dirancang untuk menjadi asisten serbaguna di server Discord Anda, membantu menjawab pertanyaan kompleks dan memberikan update cuaca terkini untuk seluruh wilayah Indonesia.

## 🔗 Invite Bot

Anda dapat mengundang bot ini ke server Anda menggunakan tautan berikut:
[**Undang Bot ke Server**](https://discord.com/oauth2/authorize?client_id=1415284153309593654&permissions=2048&response_type=code&redirect_uri=https%3A%2F%2Fbot.oxidilily.com&integration_type=0&scope=identify+bot)

## ✨ Fitur Utama

- **💬 Tanya AI (DeepSeek)**: Chat cerdas yang dapat menjawab berbagai pertanyaan, memberikan penjelasan, atau sekadar teman ngobrol.
- **🌤️ Info Cuaca BMKG**: Cek prakiraan cuaca real-time untuk desa, kecamatan, kota, hingga provinsi di Indonesia.
- **🔍 Pencarian Wilayah**: Fitur pencarian pintar untuk menemukan kode dan nama wilayah yang terdaftar di database (mendukung pencarian spesifik).
- **💓 Health Check**: Endpoint HTTP bawaan untuk monitoring uptime (kompatibel dengan Uptime Kuma) di port 99.
- **🐳 Docker Ready**: Mendukung deployment mudah menggunakan Docker.

## 📋 Prasyarat

Sebelum memulai, pastikan Anda memiliki:
- **Python 3.9+** (jika menjalankan manual)
- **Akun Discord Developer** dan Token Bot
- **API Key DeepSeek**

## 🚀 Instalasi & Konfigurasi

### 1. Clone Repository
```bash
git clone https://github.com/OxidiLily/Bot-Discord-with-Deepseek.git
cd Bot-Discord-with-Deepseek
```

### 2. Setup Environment
Buat file `.env` (atau rename `.env.example` menjadi `.env`) dan isi kredensial Anda:

```bash
BotToken=token_bot_discord_anda_disini
BotTokenDeepSeek=api_key_deepseek_anda_disini
```
*(Catatan: Pastikan nama variabel environment sesuai dengan yang ada di `main.py`)*

### 3. Instal Dependensi
Jika menjalankan secara lokal tanpa Docker:
```bash
pip install -r requirements.txt
```

## 🎮 Cara Penggunaan (Commands)

Bot menggunakan prefix `!` secara default. Berikut daftar perintah yang tersedia:

### 1. Tanya AI
Bertanya apa saja kepada AI DeepSeek.
- **Format**: `!t [pertanyaan]` atau `!tanya [pertanyaan]`
- **Contoh**: 
  - `!t Apa itu Python?`
  - `!tanya Buatkan resep nasi goreng`

### 2. Cek Cuaca
Melihat prakiraan cuaca dari BMKG. Bot akan mencari wilayah yang paling cocok.
- **Format**: `!c [nama daerah]` atau `!cuaca [nama daerah]`
- **Contoh**:
  - `!c Jakarta` (Akan mencari wilayah Jakarta)
  - `!c Kauman Batang` (Pencarian spesifik desa/kelurahan)
  
> **Tips:** Jika bot memberikan daftar pilihan wilayah (karena nama terlalu umum), gunakan nama yang lebih spesifik atau salin nama dari daftar yang diberikan.

### 3. Cari Wilayah
Mencari daftar wilayah yang tersedia di database untuk memastikan ejaan atau ketersediaan data.
- **Format**: `!w [nama wilayah]` atau `!wilayah [nama wilayah]`
- **Contoh**:
  - `!w Semarang`
  - `!wilayah Jawa Tengah`

### 4. Bantuan
Menampilkan daftar perintah dan panduan singkat.
- **Format**: `!h` atau `!help`

## 🐳 Menjalankan dengan Docker

Bot ini sudah dilengkapi dengan `Dockerfile` untuk kemudahan deployment.

1. **Build Image**
   ```bash
   docker build -t bot-discord-deepseek .
   ```

2. **Jalankan Container**
   ```bash
   docker run -d \
     --env-file .env \
     --name bot-assistant \
     -p 99:99 \
     bot-discord-deepseek
   ```
   
   *Port 99 digunakan untuk health check server.*

## 🏥 Health Check (Monitoring)

Bot menjalankan server HTTP ringan di port `99` yang bisa digunakan untuk layanan monitoring seperti **Uptime Kuma**.

- **URL**: `http://localhost:99/health`
- **Response**: JSON status `{ "status": "ok", ... }`

## 📂 Struktur Proyek

```
.
├── main.py            # Entry point bot & konfigurasi commands
├── response.py        # Handler untuk logic response AI & Cuaca
├── cuaca.py           # Modul integrasi API BMKG & Parsing Data
├── ai_assistant.py    # Modul integrasi DeepSeek API
├── message.py         # Formatter pesan Discord
├── date.py            # Helper tanggal
├── api.py             # Inisialisasi Client AI
├── Dockerfile         # Konfigurasi Docker
├── requirements.txt   # Daftar library Python
└── .env               # File konfigurasi rahasia (JANGAN DI-COMMIT)
```

## 🤝 Kontribusi

Kontribusi sangat diterima! Silakan fork repository ini dan buat Pull Request untuk fitur baru atau perbaikan bug.

## 📝 Lisensi

Dibuat oleh [OxidiLily](https://github.com/OxidiLily).
