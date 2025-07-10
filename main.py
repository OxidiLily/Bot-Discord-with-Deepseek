# install OpenAI SDK : `pip3 install openai`
import discord
from discord.ext import commands
from openai import OpenAI
import os
from dotenv import load_dotenv
import asyncio


# Mengakses API
load_dotenv()
BotDiscord  = os.getenv('BotToken')
client = OpenAI(api_key=os.getenv('API'), base_url="https://api.deepseek.com")

# Konfigurasi bot Discord
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents) 
response_salam = "🤩 Halo Master 🥰🤭, Saya siap membantu Master 🫡"
response_tanya = "Masukkan pertanyaan Master setelah !tanya. Contoh: !tanya Apa itu DeepSeek?"
response_sabar= "Oke Master, saya akan menunggu pertanyaan selanjutnya. Silakan bertanya kapan saja! 🥰🤭"

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
    
    # Cek apakah pesan dimulai dengan "halo" atau "hai"
    if (msg_content == "!tanya halo" or 
        msg_content == "!tanya hai" or 
        msg_content.startswith("halo") or 
        msg_content.startswith('hai')):
        # Kirim pesan balasan ke Discord
        await message.channel.send(response_salam)
        # Menampilkan balasan di terminal
        print(f'[Assistant]: {response_salam}')
        return  # Tambahkan return di sini agar tidak memproses command dua kali
    if (msg_content == "ada" or 
        msg_content == "iya" or 
        msg_content.startswith("oke")):
        # Jika pesan dimulai dengan "ada" atau "saya", proses command
        await message.channel.send(response_tanya )
        # Menampilkan balasan di terminal
        print(f'[Assistant]: {response_tanya}')
        return
    if (msg_content == "bentar ya" or 
        msg_content == "ok wait" or 
        msg_content.startswith("bentar") or 
        msg_content.startswith('sebentar') or 
        msg_content.startswith('oke')):
        # Jika pesan dimulai dengan "bentarya" dan "ok", proses command
        await message.channel.send(response_sabar)
        # Menampilkan balasan di terminal
        print(f'[Assistant]: {response_sabar}')
        return
    await bot.process_commands(message)
    
    
@bot.command(name="tanya")
async def tanya(ctx, *, pertanyaan: str):
    """Perintah untuk bertanya kepada DeepSeek."""
    try:
        # Mengambil event loop yang sedang berjalan
        loop = asyncio.get_running_loop()
        # Menjalankan permintaan ke API DeepSeek di thread executor agar tidak blocking
        response = await loop.run_in_executor(
            None,
            lambda: client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    # Prompt sistem untuk asisten
                    {"role": "system", "content": "You are a helpful assistant"},
                    # Pesan user yang ingin ditanyakan
                    {"role": "user", "content": pertanyaan},
                ],
                stream=False
            )
        )
        # Mengambil hasil jawaban dari response API
        hasil = response.choices[0].message.content
        # Jika hasil lebih dari 2000 karakter, bagi menjadi beberapa pesan (batas Discord)
        if len(hasil) > 2000:
            msg = ""
            bertanya_dengan_nada_lembut = f'Master, Ada yang ingin ditanyakan lagi?'
            for i in range(0, len(hasil), 2000):
                part = hasil[i:i+2000]
                if i == 0:
                    msg = await ctx.send(part)  # Kirim bagian pertama
                else:
                    msg = await msg.reply(part)  # Balas dengan bagian berikutnya
                    await ctx.send(bertanya_dengan_nada_lembut)  # Tanyakan jika ada yang ingin ditanyakan
                    print(bertanya_dengan_nada_lembut)
        else:
            await ctx.send(hasil)  # Kirim hasil jika kurang dari 2000 karakter
        # Tampilkan hasil di terminal
        print(f'[Assistant]: {hasil}')
    except Exception as e:
        # Tangani error dan kirim pesan error ke Discord
        await ctx.send(f'Terjadi kesalahan saat memproses permintaan 😖😵‍💫😵 ')
        print(f'Error: {str(e)}')

    #print(response.choices[0].message.content)

# Jalankan bot
bot.run(BotDiscord)

