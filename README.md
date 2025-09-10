# Bot Discord with Deepseek

Bot Discord with Deepseek adalah sebuah proyek bot Discord berbasis Python yang memanfaatkan layanan Deepseek untuk berbagai fitur AI, seperti chat, image generation, dan lainnya. Bot ini dapat dijalankan secara lokal maupun menggunakan Docker, sehingga mudah untuk di-deploy di berbagai lingkungan.

## Fitur

- Integrasi dengan Deepseek API untuk chat dan image generation (jika tersedia)
- Mudah dikonfigurasi melalui environment variable
- Dapat dijalankan secara langsung (`python`) maupun melalui Docker
- Pengelolaan perintah bot Discord yang modular

## Instalasi

### 1. Clone Repository

```bash
git clone https://github.com/OxidiLily/Bot-Discord-with-Deepseek.git
cd Bot-Discord-with-Deepseek
```

### 2. Instalasi Dependensi

Pastikan Python 3.9+ dan pip sudah terpasang.

```bash
pip install -r requirements.txt
```

### 3. Konfigurasi Environment

Buat file `.env` dan isi dengan konfigurasi berikut:

```
DISCORD_TOKEN=token_bot_discord_anda
DEEPSEEK_API_KEY=api_key_deepseek_anda
```

### 4. Jalankan Bot

```bash
python main.py
```

### 5. Jalankan dengan Docker (Opsional)

Jika ingin menjalankan dengan Docker:

```bash
docker build -t bot-discord-deepseek .
docker run --env-file .env bot-discord-deepseek
```

## Struktur Direktori

```
.
├── main.py
├── requirements.txt
├── Dockerfile
├── .env.example
└── ... (modul dan file pendukung lainnya)
```

## Kontribusi

Kontribusi sangat terbuka! Silakan buat issue atau pull request jika ingin menambah fitur atau memperbaiki bug.


## Kontak

Dibuat oleh [OxidiLily](https://github.com/OxidiLily).

---

> **Catatan:**  
> Pastikan untuk menjaga keamanan token dan API key Anda. Jangan membagikan file `.env` ke publik.
