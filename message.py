import re
import asyncio
import discord
from date import tanggal
def pesan(message):
    msg_content = message.content.lower()
    today = tanggal

    # Daftar pola regex untuk mendeteksi salam dan kata kunci tertentu
    unrelated = re.compile(r"^(?!.*!tanya|!t|!cuaca|!c|!w|!help|!h).+", re.IGNORECASE) # Pesan yang tidak sesuai dengan perintah !tanya atau !cuaca
    date_pattern = re.compile(r"date|-tgl", re.IGNORECASE)
    
    # Respon bot untuk setiap pola dengan Embed
    response_tidaksesuai = discord.Embed(
        title="❗ Format Perintah Tidak Sesuai ❗",
        description=f"""
        Maaf master {message.author.mention}, format yang digunakan tidak sesuai.
        
        Silahkan gunakan format berikut untuk melihat bantuan:

        `!help` | `!h` : Untuk menampilkan bantuan 🆘""",
        
        color=discord.Color.red()
    )
    # Embed untuk tanggal
    response_tanggal = discord.Embed(
        title=f"📅 Informasi Tanggal",
        description=f"""
        Hari ini adalah : 
        
        {today} 🗓️,
        
        Apakah Master {message.author.mention} ada keperluan?""",
        color=discord.Color.green()
    )

    
    # Respon otomatis untuk salam dan kata kunci tertentu menggunakan regex
    if date_pattern.search(msg_content):
        return response_tanggal
    elif unrelated.match(msg_content):
        return response_tidaksesuai
    
    return None  # kalau cocok dengan unrelated, biarkan diproses lebih lanjut
    

async def response_message(hasil, ctx):
    today = tanggal
    # Pesan penutup response dari bot
    bertanya_dengan_nada_lembut = discord.Embed(
        title=" 🤖 Konfirmasi Jawaban 🤖",
        description=f"""
        Master {ctx.author.mention}, Apakah jawaban sudah sesuai?
        Jika belum sesuai, silakan Master {ctx.author.mention} dapat tanyakan ulang dengan pertanyaan yang lebih mendetail yaa...😊🙏""",
        color=discord.Color.purple()
    )
    bertanya_cuaca = discord.Embed(
        title=" 🌤️ Informasi Cuaca 🌤️ ",
        description=f"""
        Master {ctx.author.mention}, berikut informasi cuaca yang berhasil saya dapatkan.
        Jika belum sesuai, coba cari dengan nama kelurahan/desa atau bisa kunjungi https://www.bmkg.go.id/cuaca/prakiraan-cuaca yaa...😊🙏""",
        color=discord.Color.blue()
    )
    # Cek panjang hasil jawaban, jika lebih dari 2000 karakter, bagi menjadi beberapa pesan
    if len(hasil) > 2000:
            parts = split_message(hasil)
            msg = None
            for part in parts:
                # part = hasil[i:i+2000]
                # if i == 0:
                async with ctx.typing():
                    await asyncio.sleep(2) # Simulasi delay mengetik
                    if msg is None:
                        msg = await ctx.send(f'\n{part}' )
                    else:
                        await ctx.typing()
                        await asyncio.sleep(2) # Simulasi delay mengetik
                        msg = await msg.reply(f'\n{part}' )
            async with ctx.typing():
                if "cuaca" in hasil.lower():
                    await asyncio.sleep(2) # Simulasi delay mengetik
                    await ctx.channel.send(embed=bertanya_cuaca)
                else:
                    await asyncio.sleep(2) # Simulasi delay mengetik
                    await ctx.channel.send(embed=bertanya_dengan_nada_lembut) 
    else:
        await ctx.typing()
        async with ctx.typing():
            await ctx.send(hasil)
            if "cuaca" in hasil.lower():
                await asyncio.sleep(2) # Simulasi delay mengetik
                await ctx.channel.send(embed=bertanya_cuaca)
            else:
                await asyncio.sleep(2) # Simulasi delay mengetik
                await ctx.channel.send(embed=bertanya_dengan_nada_lembut) 
    #await asyncio.sleep(2)
    print(f'{today} [Assistant]: {hasil}')

    
def split_message(text, limit=2000):
    parts = []
    while len(text) > limit:
        split_pos = text.rfind("\n", 0, limit)  # cari newline sebelum limit
        if split_pos == -1:
            split_pos = limit
        parts.append(text[:split_pos])
        text = text[split_pos:].lstrip()
    parts.append(text)
    return parts
