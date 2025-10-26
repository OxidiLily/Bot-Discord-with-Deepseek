import aiohttp
import csv
from io import StringIO
import traceback
import discord
from date import tanggal
import asyncio
from message import response_message
from api import AI

URL_WILAYAH = "https://raw.githubusercontent.com/kodewilayah/permendagri-72-2019/main/dist/base.csv"
URL_BMKG_API = "https://api.bmkg.go.id/publik/prakiraan-cuaca"

# Cache untuk menyimpan data wilayah
wilayah_cache = []

async def load_wilayah_data():
    """Load data wilayah dari CSV dan simpan di cache"""
    global wilayah_cache
    if wilayah_cache:
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

def convert_kode_format(kode):
    """Konversi format kode dari XX.XX.XX.XXXX menjadi berbagai format yang mungkin"""
    formats = []
    
    # Pastikan kode adalah level 4 (kelurahan/desa)
    parts = kode.split('.')
    if len(parts) != 4:
        print(f"  Warning: Kode bukan level 4, memiliki {len(parts)} segmen")
        return [kode]
    
    # Format 1: Dengan titik seperti aslinya (XX.XX.XX.XXXX)
    formats.append(kode)
    
    # Format 2: Tanpa titik (XXXXXXXXXXXX)
    formats.append(kode.replace('.', ''))
    
    # Format 3: Gabungan dengan padding (untuk memastikan format konsisten)
    # Contoh: 11.03.07.2001 -> 11030720001 (jika segment terakhir perlu 5 digit)
    kode_clean = kode.replace('.', '')
    if len(kode_clean) == 10:
        formats.append(kode_clean)
        # Coba juga dengan segment terakhir yang di-pad
        formats.append(f"{parts[0]}{parts[1]}{parts[2]}{parts[3]:0>4}")
    
    # Format 4: Dengan titik tapi segment terakhir di-pad 4 digit
    formats.append(f"{parts[0]}.{parts[1]}.{parts[2]}.{parts[3]:0>4}")
    
    # Hapus duplikat sambil mempertahankan urutan
    seen = set()
    unique_formats = []
    for fmt in formats:
        if fmt not in seen:
            seen.add(fmt)
            unique_formats.append(fmt)
    
    return unique_formats

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
            # Jika kode tidak lengkap (level 3 atau kurang), cari kelurahan di bawahnya
            if kode.count('.') < 3:
                print(f"  Kode tidak lengkap ({kode.count('.')} segmen), mencari kelurahan...")
                kelurahan = cari_kelurahan_di_wilayah(kode)
                if kelurahan:
                    print(f"  Menggunakan kelurahan: {kelurahan[1]} ({kelurahan[0]})")
                    return kelurahan[0], kelurahan[1]
            return kode, wilayah
    
    # 2. Starts with match
    for kode, wilayah in wilayah_cache:
        if wilayah.lower().startswith(nama_lower):
            hasil_pencarian.append((kode, wilayah, 90))
    
    # 3. Contains match
    for kode, wilayah in wilayah_cache:
        if nama_lower in wilayah.lower():
            if not any(h[0] == kode for h in hasil_pencarian):
                hasil_pencarian.append((kode, wilayah, 80))
    
    # 4. Word-by-word match
    kata_pencarian = nama_lower.split()
    if len(kata_pencarian) > 1:
        for kode, wilayah in wilayah_cache:
            wilayah_lower = wilayah.lower()
            match_count = sum(1 for kata in kata_pencarian if kata in wilayah_lower)
            
            if match_count == len(kata_pencarian):
                if not any(h[0] == kode for h in hasil_pencarian):
                    score = 85 + (match_count * 5)
                    hasil_pencarian.append((kode, wilayah, score))
    
    # 5. Partial match dengan scoring
    for kode, wilayah in wilayah_cache:
        wilayah_lower = wilayah.lower()
        score = 0
        
        for kata in kata_pencarian if len(kata_pencarian) > 1 else [nama_lower]:
            if kata in wilayah_lower:
                score += 15
            else:
                for wilayah_word in wilayah_lower.split():
                    if kata in wilayah_word or wilayah_word in kata:
                        score += 5
        
        if score >= 15:
            if not any(h[0] == kode for h in hasil_pencarian):
                hasil_pencarian.append((kode, wilayah, score))
    
    # Sort berdasarkan score dan ambil yang terbaik
    if hasil_pencarian:
        hasil_pencarian.sort(key=lambda x: x[2], reverse=True)
        best_match = hasil_pencarian[0]
        print(f"Best match found: {best_match[1]} ({best_match[0]}) with score {best_match[2]}")
        
        # Jika kode tidak lengkap (bukan level 4), cari kelurahan di bawahnya
        if best_match[0].count('.') < 3:
            print(f"  Kode tidak lengkap, mencari kelurahan...")
            kelurahan = cari_kelurahan_di_wilayah(best_match[0])
            if kelurahan:
                print(f"  Menggunakan kelurahan: {kelurahan[1]} ({kelurahan[0]})")
                return kelurahan[0], kelurahan[1]
        
        return best_match[0], best_match[1]
    
    print("No match found")
    return None, None

def cari_kelurahan_di_wilayah(kode_parent):
    """Cari kelurahan/desa pertama di bawah wilayah tertentu"""
    if not wilayah_cache:
        return None
    
    # Cari semua kelurahan yang kodenya dimulai dengan kode_parent
    kelurahan_list = []
    for kode, wilayah in wilayah_cache:
        # Cek apakah kode ini adalah child dari kode_parent dan merupakan level 4
        if kode.startswith(kode_parent + '.') and kode.count('.') == 3:
            kelurahan_list.append((kode, wilayah))
    
    # Ambil kelurahan pertama jika ada
    if kelurahan_list:
        print(f"  Ditemukan {len(kelurahan_list)} kelurahan di wilayah ini")
        return kelurahan_list[0]
    
    return None

async def get_cuaca(kode, wilayah_name):
    """Ambil data cuaca dari API BMKG resmi dengan berbagai format kode"""
    try:
        # Generate berbagai format kode yang mungkin
        kode_formats = convert_kode_format(kode)
        
        print(f"Mencoba {len(kode_formats)} format kode untuk {wilayah_name}:")
        for fmt in kode_formats:
            print(f"  - {fmt}")
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            # Coba setiap format kode
            for kode_variant in kode_formats:
                url = f"{URL_BMKG_API}?adm4={kode_variant}"
                print(f"\nMencoba URL: {url}")
                
                try:
                    async with session.get(url) as resp:
                        print(f"  Status: {resp.status}")
                        content_type = resp.headers.get('Content-Type', '')
                        print(f"  Content-Type: {content_type}")
                        
                        if resp.status == 200:
                            # Cek apakah response adalah JSON
                            if 'application/json' in content_type:
                                data = await resp.json()
                                
                                # Validasi struktur data
                                if data and isinstance(data, dict):
                                    # Cek apakah ada data lokasi dan cuaca
                                    if "lokasi" in data and "data" in data:
                                        if data["data"] and len(data["data"]) > 0:
                                            print(f"  ✓ Berhasil! Ditemukan data cuaca yang valid")
                                            return data
                                        else:
                                            print(f"  ✗ Data array kosong")
                                    else:
                                        print(f"  ✗ Struktur data tidak sesuai: {list(data.keys())}")
                                else:
                                    print(f"  ✗ Response bukan dict yang valid")
                            else:
                                # Bukan JSON, kemungkinan HTML error page
                                text = await resp.text()
                                print(f"  ✗ Response bukan JSON (Content-Type: {content_type})")
                                if len(text) < 500:
                                    print(f"  Response: {text[:200]}")
                        
                        elif resp.status == 404:
                            print(f"  ✗ Kode tidak ditemukan (404)")
                        else:
                            print(f"  ✗ Status error: {resp.status}")
                    
                    # Small delay antar request
                    await asyncio.sleep(0.3)
                    
                except Exception as e:
                    print(f"  ✗ Error: {e}")
                    continue
            
            # Jika semua format gagal, coba dengan kode yang lebih umum (kabupaten/kota)
            parts = kode.split('.')
            if len(parts) >= 2:
                # Coba dengan kode kabupaten (2 segment pertama)
                kode_kab = f"{parts[0]}.{parts[1]}"
                kode_kab_formats = [
                    kode_kab,
                    kode_kab.replace('.', ''),
                    f"{parts[0]}{parts[1]}",
                ]
                
                print(f"\n=== Mencoba kode kabupaten/kota: {kode_kab} ===")
                for kode_variant in kode_kab_formats:
                    url = f"{URL_BMKG_API}?adm4={kode_variant}"
                    print(f"Mencoba: {url}")
                    
                    try:
                        async with session.get(url) as resp:
                            if resp.status == 200 and 'application/json' in resp.headers.get('Content-Type', ''):
                                data = await resp.json()
                                if data and "lokasi" in data and "data" in data and data["data"]:
                                    print(f"✓ Berhasil dengan kode kabupaten!")
                                    return data
                    except:
                        continue
                    
                    await asyncio.sleep(0.3)
        
        print(f"\n✗ Tidak ada data cuaca ditemukan untuk {wilayah_name} dengan semua format kode")
        return None
        
    except Exception as e:
        print(f"Error in get_cuaca: {e}")
        
        traceback.print_exc()
        return None

async def format_cuaca_data(data):
    """Format data cuaca dari API BMKG menjadi teks yang mudah dibaca"""
    try:
        if not data or "lokasi" not in data or "data" not in data:
            return None
        
        lokasi = data.get("lokasi", {})
        cuaca_data = data.get("data", [])
        
        if not cuaca_data:
            return None
        
        info = []
        
        # Informasi lokasi
        desa = lokasi.get("desa", "N/A")
        kecamatan = lokasi.get("kecamatan", "N/A")
        kotkab = lokasi.get("kotkab", "N/A")
        provinsi = lokasi.get("provinsi", "N/A")
        
        info.append(f"📍 Lokasi: {desa}, {kecamatan}, {kotkab}, {provinsi}")
        info.append(f"🌐 Koordinat: {lokasi.get('lat', 'N/A')}, {lokasi.get('lon', 'N/A')}")
        info.append("")
        
        # Ambil prakiraan cuaca (data pertama saja karena struktur bisa nested)
        prakiraan_list = cuaca_data[0].get("cuaca", [[]])[0] if cuaca_data else []
        
        if not prakiraan_list:
            return None
        
        info.append("🌤️ Prakiraan Cuaca (24 jam ke depan):")
        info.append("")
        
        # Ambil 4-6 forecast pertama (sepanjang hari)
        for i, forecast in enumerate(prakiraan_list[:6], 1):
            waktu = forecast.get("local_datetime", "N/A")
            cuaca_desc = forecast.get("weather_desc", "N/A")
            suhu = forecast.get("t", "N/A")
            kelembaban = forecast.get("hu", "N/A")
            kec_angin = forecast.get("ws", "N/A")
            arah_angin = forecast.get("wd", "N/A")
            
            info.append(f"Waktu {i}: {waktu}")
            info.append(f"  • Cuaca: {cuaca_desc}")
            info.append(f"  • Suhu: {suhu}°C")
            info.append(f"  • Kelembaban: {kelembaban}%")
            info.append(f"  • Angin: {kec_angin} km/jam dari {arah_angin}")
            info.append("")
        
        return "\n".join(info)
    except Exception as e:
        print(f"Error formatting cuaca data: {e}")
        
        traceback.print_exc()
        return None

async def ringkas_cuaca(data, daerah):
    """Ringkas data cuaca dengan DeepSeek"""
    try:
        # Format data cuaca terlebih dahulu
        formatted_data = await format_cuaca_data(data)
        
        if not formatted_data:
            return f"Maaf, tidak dapat memformat data cuaca untuk {daerah}."
        
        loop = asyncio.get_running_loop()
        
        prompt = f"Ringkas prakiraan cuaca BMKG berikut dalam bahasa Indonesia yang ramah dan mudah dipahami (maksimal 7 kalimat). Sertakan emoji cuaca yang sesuai dan berikan tips singkat:\n\n{formatted_data}"
        
        response = await loop.run_in_executor(
            None,
            lambda: AI.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "Kamu adalah asisten cuaca ramah yang memberikan ringkasan informatif dalam bahasa Indonesia. Fokus pada: kondisi cuaca, suhu, kelembaban, dan saran aktivitas. Gunakan emoji cuaca (🌤️☀️🌧️⛈️☁️🌥️💨🌡️💧)."},
                    {"role": "user", "content": prompt}
                ],
                stream=False
            )
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in ringkas_cuaca: {e}")
        traceback.print_exc()
        return f"Maaf, terjadi kesalahan saat memproses data cuaca untuk {daerah}."

async def cuaca(ctx, *, daerah: str):
    """Perintah untuk mendapatkan prakiraan cuaca dari BMKG."""
    async with ctx.typing():
        try:
            print(f'{tanggal} [Assistant]:')
            print(50 * "=")
            print(f"=== CUACA REQUEST: {daerah} ===")
            
            # Cari kode wilayah
            kode, wilayah = await cari_wilayah_terbaik(daerah)
            
            if not kode:
                embed = discord.Embed(
                    title="❌ Wilayah Tidak Ditemukan",
                    description=f"Maaf, wilayah '{daerah}' tidak ditemukan dalam database.\n\nPastikan ejaan sudah benar atau coba dengan nama yang lebih spesifik.\n\n**Contoh:** Jakarta, Bandung, Surabaya, Pemalang, Semarang",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                print(f'{tanggal} [Assistant]: Wilayah {daerah} tidak ditemukan')
                return
            
            print(f"Wilayah ditemukan: {wilayah} (Kode: {kode})")
            
            # Ambil data cuaca
            data = await get_cuaca(kode, wilayah)
            
            if not data:
                embed = discord.Embed(
                    title="⚠️ Data Cuaca Tidak Tersedia",
                    description=f"Maaf, data cuaca untuk **{wilayah}** tidak tersedia saat ini dari BMKG.\n\n**Kemungkinan penyebab:**\n• Data belum tersedia untuk wilayah tingkat kelurahan/desa\n• Coba gunakan nama kota/kabupaten yang lebih umum\n• Gangguan sementara pada server BMKG\n\n**Saran:**\nGunakan command `!w {daerah}` untuk melihat wilayah yang tersedia.",
                    color=discord.Color.orange()
                )
                embed.add_field(name="Kode Wilayah", value=f"`{kode}`", inline=True)
                embed.add_field(name="Nama Wilayah", value=wilayah, inline=True)
                embed.set_footer(text="Data cuaca dari BMKG • Coba dengan nama yang lebih umum")
                await ctx.send(embed=embed)
                print(f'{tanggal} [Assistant]: Data cuaca tidak tersedia untuk {wilayah}')
                return
            
            print(f"✓ Data cuaca berhasil diambil untuk {wilayah}")
            print(50 * "=")
            
            # Ringkas dengan AI
            hasil = await ringkas_cuaca(data, wilayah)
            
            # Kirim hasil
            async with ctx.typing():
                await asyncio.sleep(2)
                await response_message(hasil, ctx)
                print(f'{tanggal} [Assistant]: Cuaca berhasil dikirim untuk {wilayah}')
            
        except Exception as e:
            async with ctx.typing():
                await ctx.send("Gagal mengambil data cuaca dari BMKG 😵")
                print(f'Error in cuaca function: {str(e)}')
                
                traceback.print_exc()
                print(f'{tanggal} [Assistant]: Gagal mengambil data cuaca dari BMKG 😵')

async def get_kode_wilayah(nama):
    """Fungsi untuk mendapatkan kode wilayah (backward compatibility)"""
    return await cari_wilayah_terbaik(nama)