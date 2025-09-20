from datetime import datetime
import re
import asyncio
import discord

def pesan(message):
    msg_content = message.content.lower()
    today = datetime.now().strftime("%A, %d %B %Y")

    # Daftar pola regex untuk mendeteksi salam dan kata kunci tertentu
    unrelated = re.compile(r"^(?!.*!tanya|!t|!cuaca|!c).+", re.IGNORECASE) # Pesan yang tidak sesuai dengan perintah !tanya atau !cuaca
    help_pattern = re.compile(r"^help|-h", re.IGNORECASE) # Pola untuk mendeteksi perintah bantuan
    date_pattern = re.compile(r"date|-tgl", re.IGNORECASE)
    
    # Respon bot untuk setiap pola
    response_tidaksesuai = discord.Embed(
        title="❗ Format Pertanyaan Tidak Sesuai ❗",
        description=f"""Maaf master {message.author.mention}, format pertanyaan tidak sesuai.
        Silahkan gunakan format berikut untuk melihat bantuan:

        help | -h : Untuk menampilkan bantuan 🆘""",
        color=discord.Color.red()
    )

    response_tanggal = discord.Embed(
        title=f"📅 Informasi Tanggal",
        description=f"""
        Hari ini adalah : 
        {today} 🗓️, \n\n Apakah Master {message.author.mention} ada keperluan?""",
        color=discord.Color.green()
    )
    
    # Embed untuk help
    response_help = discord.Embed(
        title="📖 Bantuan Perintah",
        description=f"""
            Halo Master {message.author.mention}, gunakan format berikut:

            **!tanya [pertanyaan]**  atau **!t [pertanyaan]**
            Contoh: `!tanya Apa itu AI?`

            **!cuaca [nama daerah]**  atau **!c [nama daerah]**
            Contoh: `!cuaca Jakarta`

            **date** atau **-tgl**  
            Untuk menanyakan tanggal hari ini 🗓️
            """,
        color=discord.Color.blue()
    )

    
    # Respon otomatis untuk salam dan kata kunci tertentu menggunakan regex
    if help_pattern.match(msg_content):
        return response_help
    elif date_pattern.search(msg_content):
        return response_tanggal
    elif unrelated.match(msg_content):
        return response_tidaksesuai
    
    return None  # kalau cocok dengan !tanya, biarkan diproses lebih lanjut
    

async def response_message(hasil, ctx):
    today = datetime.now().strftime("%d %B %Y")
    # Pesan penutup response dari bot
    bertanya_dengan_nada_lembut = discord.Embed(
        title=" 🤖 Konfirmasi Jawaban 🤖",
        description=f"""Master {ctx.author.mention}, Apakah jawaban sudah sesuai?
        Jika belum sesuai, silakan Master {ctx.author.mention} dapat tanyakan lagi dengan pertanyaan yang mendetail yaa...😊🙏""",
        color=discord.Color.purple()
    )
    
    # Cek panjang hasil jawaban, jika lebih dari 2000 karakter, bagi menjadi beberapa pesan
    if len(hasil) > 2000:
            msg = None
            for i in range(0, len(hasil), 2000):
                part = hasil[i:i+2000]
                if i == 0:
                    await ctx.typing()
                    await asyncio.sleep(2) # Simulasi delay mengetik
                    msg = await ctx.send(f'\n{part}' )
                else:
                    await ctx.typing()
                    await asyncio.sleep(2) # Simulasi delay mengetik
                    msg = await msg.reply(f'\n{part}' )
            await ctx.typing()
            await asyncio.sleep(2) # Simulasi delay mengetik
            await ctx.send(bertanya_dengan_nada_lembut)
    else:
        await ctx.typing()
        await asyncio.sleep(2) # Simulasi delay mengetik
        await ctx.send(hasil)
        await ctx.typing()
        await asyncio.sleep(2) # Simulasi delay mengetik
        await ctx.send(f'\n{bertanya_dengan_nada_lembut}')
    #await asyncio.sleep(2)
    print(f'{today} [Assistant]: {hasil}')

    
