# install OpenAI SDK : `pip3 install openai`
import discord
from discord.ext import commands
from openai import OpenAI
import os
from dotenv import load_dotenv
import asyncio
from datetime import datetime
import re
# Mengakses API
load_dotenv()
BotDiscord  = os.getenv('BotToken')
client = OpenAI(api_key=os.getenv('API'), base_url="https://api.deepseek.com")

# Konfigurasi bot Discord
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents) 


@bot.event
async def on_ready():
    print(f'Bot {bot.user.name} telah siap!')

@bot.event
async def on_message(message):
    msg_content = message.content.lower()
    # Menghindari loop tak terbatas
    if message.author == bot.user:
        return
    # Pisahkan antara pesan dari oxidilily dan OxidiLily Assistant#9815
    if str(message.author) == "OxidiLily Assistant#9815":
        print(f'[Assistant]: {message.content}')
    else :
        # Jika pesan dimulai dengan "!tanya", pisahkan pertanyaan
        if "!tanya " not in message.content:
            print(f'[Owner]: {message.content}')
        else:
            print(f'[Owner]: {message.content.split("!tanya ",1)[1]}')
    
    # Daftar pola regex untuk mendeteksi salam dan kata kunci tertentu
    unrelated = re.compile(r"^(?!.*!tanya).+", re.IGNORECASE)
    salam_pattern = re.compile(r"^!tanya\s*(halo|hai)$|^(halo|hai|p)\b", re.IGNORECASE)
    tanya_pattern = re.compile(r"^(ada|iya)$|^oke\b", re.IGNORECASE)
    sabar_pattern = re.compile(r"^(bentar ya|ok wait)$|^(bentar|sebentar|oke)\b", re.IGNORECASE)
    tanggal_pattern = re.compile(r"^(tanggal berapa hari ini|hari ini tanggal berapa| !tanya hari ini tanggal| !tanya dino iki)$|^(tanggal|hari ini|tgl)\b", re.IGNORECASE)

    # Respon bot untuk setiap pola
    response_salam = f"🤩 Halo Master {message.author} 🥰🤭, Saya siap membantu Master 🫡"
    response_tanya = f"Masukkan pertanyaan Master {message.author}, saya akan berusaha menjawabnya dengan sebaik mungkin. 🥰🤭"
    response_sabar= f"Oke Master {message.author}, saya akan menunggu pertanyaan selanjutnya. Silakan bertanya kapan saja! 🥰🤭"
    today = datetime.now().strftime("%A, %d %B %Y")
    
    # Respon otomatis untuk salam dan kata kunci tertentu menggunakan regex
    if salam_pattern.match(msg_content):
        async with message.channel.typing():
            await message.channel.send(response_salam)
        print(f'[Assistant]: {response_salam}')
        return
    if tanya_pattern.match(msg_content):
        async with message.channel.typing():
            await message.channel.send(response_tanya)
        print(f'[Assistant]: {response_tanya}')
        return
    if sabar_pattern.match(msg_content):
        async with message.channel.typing():
            await message.channel.send(response_sabar)
        print(f'[Assistant]: {response_sabar}')
        return
    if tanggal_pattern.match(msg_content):
        async with message.channel.typing():
            await message.channel.send(f'Hari ini tanggal {today} 🗓️, Apakah Master {message.author} ada keperluan?')
        print(f'[Assistant]: Hari ini tanggal {today} 🗓️, Apakah Master ada keperluan?')
        return
    if unrelated.match(msg_content):
        async with message.channel.typing():
            await message.channel.send(f'Halo Master {message.author}, untuk menggunakan fitur tanya jawab, silakan ketik perintah dengan format:\n\n !tanya [pertanyaan yang ingin ditanyakan oleh {message.author}].\n\n Contohnya: !tanya Apa itu DeepSeek?\n\n Dengan format ini, sistem akan memahami pertanyaan {message.author} dan memberikan jawaban yang sesuai.')
        print(f'Halo Master {message.author}, untuk menggunakan fitur tanya jawab, silakan ketik perintah dengan format: !tanya [pertanyaan yang ingin ditanyakan oleh {message.author}]. Contohnya: !tanya Apa itu DeepSeek? Dengan format ini, sistem akan memahami pertanyaan {message.author} dan memberikan jawaban yang sesuai.')
        return

    await bot.process_commands(message)
    
    
@bot.command(name="tanya")
async def tanya(ctx, *, pertanyaan: str):
    """Perintah untuk bertanya kepada DeepSeek."""
    try:
        async with ctx.typing():  # Bot mengetik saat menunggu jawaban AI
            # Mengambil event loop yang sedang berjalan
            loop = asyncio.get_running_loop()
            # Menjalankan permintaan ke API DeepSeek di thread executor agar tidak blocking
            response = await loop.run_in_executor(
                None,
                lambda: client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant"},
                        {"role": "user", "content": pertanyaan},
                    ],
                    stream=False
                )
            )
        # Pesan penutup dengan nada lembut
        bertanya_dengan_nada_lembut = f'Master {ctx.author}, Ada yang ingin ditanyakan lagi?'
        # Mengambil hasil jawaban dari response API
        hasil = response.choices[0].message.content
        async with ctx.typing():  # Menunjukkan bot sedang mengetik saat memproses hasil
            if len(hasil) > 2000:
                msg = None
                for i in range(0, len(hasil), 2000):
                    part = hasil[i:i+2000]
                    if i == 0:
                        await ctx.typing()
                        await asyncio.sleep(2) # Simulasi delay mengetik
                        msg = await ctx.send(part)
                    else:
                        await ctx.typing()
                        await asyncio.sleep(2) # Simulasi delay mengetik
                        msg = await msg.reply(part)
                await ctx.typing()
                await asyncio.sleep(2) # Simulasi delay mengetik
                await ctx.send(bertanya_dengan_nada_lembut)
                print(bertanya_dengan_nada_lembut)
            else:
                await ctx.typing()
                await asyncio.sleep(2) # Simulasi delay mengetik
                await ctx.send(hasil)
                await ctx.typing()
                await asyncio.sleep(2) # Simulasi delay mengetik
                await ctx.send(bertanya_dengan_nada_lembut)
        print(f'[Assistant]: {hasil}')
    except Exception as e:
        async with ctx.typing():
            await asyncio.sleep(1)
        await ctx.send(f'Terjadi kesalahan saat memproses permintaan 😖😵‍💫😵 ')
        print(f'Error: {str(e)}')


if __name__ == "__main__":
    bot.run(BotDiscord)