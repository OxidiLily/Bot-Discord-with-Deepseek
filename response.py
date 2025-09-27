from message import response_message
import asyncio
import aiohttp
import csv
from io import StringIO
from openai import OpenAI
import os
from dotenv import load_dotenv
from date import tanggal
import discord

load_dotenv()
AI = OpenAI(api_key=os.getenv('API'), base_url="https://api.deepseek.com")

async def tanya(ctx, *, tanya: str):
    """Perintah untuk bertanya kepada DeepSeek."""
    try:
        async with ctx.typing():  # Bot mengetik saat menunggu jawaban AI
            # Mengambil event loop yang sedang berjalan
            loop = asyncio.get_running_loop()
            # Menjalankan permintaan ke API DeepSeek di thread executor agar tidak blocking
            response = await loop.run_in_executor(
                None,
                lambda: AI.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant"},
                        {"role": "user", "content": tanya},
                    ],
                    stream=False
                )
            )
        # Mengambil hasil jawaban dari response API
        hasil = response.choices[0].message.content
        async with ctx.typing():  # Menunjukkan bot sedang mengetik saat memproses hasil
            # Mengirimkan hasil jawaban ke channel Discord
            await response_message(hasil, ctx)
    except Exception as e:
        async with ctx.typing():
            await ctx.send(f'Terjadi kesalahan saat memproses permintaan 😖😵‍💫😵 ')
            print(f'Error: {str(e)}')

URL_WILAYAH = "https://raw.githubusercontent.com/kodewilayah/permendagri-72-2019/main/dist/base.csv"
URL_BMKG = "https://api.bmkg.go.id/publik/prakiraan-cuaca"

# Cache untuk menyimpan data wilayah
wilayah_cache = []

async def load_wilayah_data():
    """Load data wilayah dari CSV dan simpan di cache"""
    global wilayah_cache
    if wilayah_cache:  # Jika sudah ada di cache, tidak perlu download lagi
        return wilayah_cache
    
    try:
        print("Loading wilayah data...")
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            async with session.get(URL_WILAYAH) as resp:
                if resp.status != 200:
                    print(f"Error downloading wilayah data: {resp.status}")
                    return []
                
                text = await resp.text()
                reader = csv.reader(StringIO(text))
                next(reader)  # skip header
                
                for row in reader:
                    if len(row) >= 2:
                        kode, wilayah = row[0], row[1]
                        wilayah_cache.append((kode, wilayah))
                
                print(f"Loaded {len(wilayah_cache)} wilayah data")
                return wilayah_cache
    except Exception as e:
        print(f"Error loading wilayah data: {e}")
        return []

async def cari_wilayah_terbaik(nama):
    """Cari wilayah terbaik dengan algoritma yang diperbaiki"""
    await load_wilayah_data()
    
    if not wilayah_cache:
        return None, None
    
    nama_lower = nama.lower().strip()
    hasil_pencarian = []
    
    print(f"Mencari wilayah untuk: '{nama}'")
    
    # 1. Exact match (prioritas tertinggi)
    for kode, wilayah in wilayah_cache:
        if nama_lower == wilayah.lower():
            print(f"Exact match found: {wilayah} ({kode})")
            return kode, wilayah
    
    # 2. Starts with match
    for kode, wilayah in wilayah_cache:
        if wilayah.lower().startswith(nama_lower):
            hasil_pencarian.append((kode, wilayah, 90))
    
    # 3. Contains match (untuk kasus seperti "Jakarta Utara" yang ada di "Kota Jakarta Utara")
    for kode, wilayah in wilayah_cache:
        if nama_lower in wilayah.lower():
            # Cek apakah sudah ada di hasil
            if not any(h[0] == kode for h in hasil_pencarian):
                hasil_pencarian.append((kode, wilayah, 80))
    
    # 4. Word-by-word match (untuk "Jakarta Utara" cocok dengan "Kota Jakarta Utara")
    kata_pencarian = nama_lower.split()
    if len(kata_pencarian) > 1:
        for kode, wilayah in wilayah_cache:
            wilayah_lower = wilayah.lower()
            match_count = sum(1 for kata in kata_pencarian if kata in wilayah_lower)
            
            # Jika semua kata ditemukan
            if match_count == len(kata_pencarian):
                if not any(h[0] == kode for h in hasil_pencarian):
                    score = 85 + (match_count * 5)  # Bonus untuk lebih banyak kata yang cocok
                    hasil_pencarian.append((kode, wilayah, score))
    
    # 5. Partial match dengan scoring
    for kode, wilayah in wilayah_cache:
        wilayah_lower = wilayah.lower()
        score = 0
        
        # Hitung similarity berdasarkan kata yang cocok
        for kata in kata_pencarian if len(kata_pencarian) > 1 else [nama_lower]:
            if kata in wilayah_lower:
                score += 15
            else:
                # Cek partial match untuk typo
                for wilayah_word in wilayah_lower.split():
                    if kata in wilayah_word or wilayah_word in kata:
                        score += 5
        
        if score >= 15:  # Threshold minimal untuk dianggap match
            if not any(h[0] == kode for h in hasil_pencarian):
                hasil_pencarian.append((kode, wilayah, score))
    
    # Sort berdasarkan score dan ambil yang terbaik
    if hasil_pencarian:
        hasil_pencarian.sort(key=lambda x: x[2], reverse=True)
        print(f"Best match found: {hasil_pencarian[0][1]} ({hasil_pencarian[0][0]}) with score {hasil_pencarian[0][2]}")
        return hasil_pencarian[0][0], hasil_pencarian[0][1]
    
    print("No match found")
    return None, None

async def test_bmkg_api(kode, wilayah_name):
    """Test BMKG API dengan berbagai parameter dan format"""
    test_configs = [
        {"url": f"{URL_BMKG}?adm4={kode}", "desc": f"adm4={kode}"},
        {"url": f"{URL_BMKG}?adm3={kode}", "desc": f"adm3={kode}"},
        {"url": f"{URL_BMKG}?adm2={kode}", "desc": f"adm2={kode}"},
        {"url": f"{URL_BMKG}?adm1={kode}", "desc": f"adm1={kode}"},
        # Coba dengan kode 6 digit pertama (untuk kota/kabupaten)
        {"url": f"{URL_BMKG}?adm4={kode[:6]}", "desc": f"adm4={kode[:6]} (6 digit)"},
        {"url": f"{URL_BMKG}?adm3={kode[:6]}", "desc": f"adm3={kode[:6]} (6 digit)"},
        # Coba dengan kode 4 digit pertama (untuk provinsi)
        {"url": f"{URL_BMKG}?adm2={kode[:4]}", "desc": f"adm2={kode[:4]} (4 digit)"},
    ]
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
        for config in test_configs:
            try:
                print(f"Testing BMKG API: {config['desc']}")
                async with session.get(config["url"]) as resp:
                    print(f"Status: {resp.status} for {config['desc']}")
                    
                    if resp.status == 200:
                        data = await resp.json()
                        if data and isinstance(data, dict) and "data" in data:
                            if data["data"] and len(data["data"]) > 0:
                                print(f"Success! Found weather data with {config['desc']}")
                                return data
                            else:
                                print(f"Empty data array for {config['desc']}")
                        else:
                            print(f"Invalid data structure for {config['desc']}")
                    
                    # Small delay between requests
                    await asyncio.sleep(0.5)
                    
            except Exception as e:
                print(f"Error testing {config['desc']}: {e}")
                continue
    
    print(f"No weather data found for {wilayah_name} (kode: {kode})")
    return None

async def get_kode_wilayah(nama):
    """Fungsi untuk mendapatkan kode wilayah (backward compatibility)"""
    return await cari_wilayah_terbaik(nama)

async def get_cuaca(kode, wilayah_name):
    """Ambil data cuaca dengan testing berbagai parameter"""
    return await test_bmkg_api(kode, wilayah_name)

async def ringkas_cuaca(data, daerah):
    """Ringkas data cuaca dengan DeepSeek"""
    try:
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None,
            lambda: AI.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "Kamu adalah asisten ramah yang merangkum prakiraan cuaca BMKG menjadi bahasa yang mudah dipahami. Berikan ringkasan cuaca dalam bahasa Indonesia yang informatif dan mudah dimengerti."},
                    {"role": "user", "content": f"Ringkas data cuaca untuk {daerah}: {data}"}
                ],
                stream=False
            )
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in ringkas_cuaca: {e}")
        return f"Maaf, terjadi kesalahan saat memproses data cuaca untuk {daerah}."

async def cuaca(ctx, *, daerah: str):
    """Perintah untuk mendapatkan prakiraan cuaca dari BMKG."""
    async with ctx.typing():
        try:
            print(f'{tanggal} [Assistant]:')
            print(50 * "=")
            print(f"=== CUACA REQUEST: {daerah} ===")
            
            # Cari kode wilayah
            kode, wilayah = await get_kode_wilayah(daerah)
            
            if not kode:
                embed = discord.Embed(
                    title="❌ Wilayah Tidak Ditemukan",
                    description=f"Maaf, wilayah '{daerah}' tidak ditemukan dalam database.\n\nPastikan ejaan sudah benar atau coba dengan nama yang lebih spesifik.\n\nContoh: Jakarta, Bandung, Surabaya, Jakarta Utara",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                print(f'{tanggal} [Assistant]: Wilayah {daerah} tidak ditemukan')
                return
            
            print(f"Wilayah ditemukan: {wilayah} (Kode: {kode})")
            
            # Ambil data cuaca
            data = await get_cuaca(kode, wilayah)
            
            if not data or "data" not in data or not data["data"]:
                print(f"Gagal mendapatkan data cuaca untuk {wilayah}")
                
                # Coba mencari alternatif yang lebih umum
                if len(kode) > 6:
                    print("Mencoba dengan kode wilayah yang lebih umum...")
                    data = await get_cuaca(kode[:6], wilayah)
                
                if not data or "data" not in data or not data["data"]:
                    embed = discord.Embed(
                        title="⚠️ Data Cuaca Tidak Tersedia",
                        description=f"Maaf, data cuaca untuk '{wilayah}' tidak tersedia saat ini dari BMKG.\n\n**Kemungkinan penyebab:**\n• Wilayah terlalu spesifik\n• Data belum tersedia di BMKG\n• Gangguan sementara pada server BMKG\n\n**Saran:**\nCoba dengan nama wilayah yang lebih umum (misal: nama kota/kabupaten).",
                        color=discord.Color.orange()
                    )
                    embed.add_field(name="Kode Wilayah", value=kode, inline=True)
                    embed.add_field(name="Nama Wilayah", value=wilayah, inline=True)
                    await ctx.send(embed=embed)
                    print(f'{tanggal} [Assistant]: Data cuaca tidak tersedia untuk {wilayah}')
                    return
            
            print(f"Data cuaca berhasil diambil untuk {wilayah}")
            print(50 * "=")
            
            # Ringkas dengan AI
            hasil = await ringkas_cuaca(data, wilayah)
            
            # Kirim hasil dalam format yang sudah ada
            async with ctx.typing():
                await asyncio.sleep(2) # Simulasi delay mengetik
                await response_message(hasil, ctx)
                print(f'{tanggal} [Assistant]: Cuaca berhasil dikirim untuk {wilayah}')
            
        except Exception as e:
            async with ctx.typing():
                await ctx.send("Gagal mengambil data cuaca dari BMKG 😵")
                print(f'Error in cuaca function: {str(e)}')
                print(f'{tanggal} [Assistant]: Gagal mengambil data cuaca dari BMKG 😵')