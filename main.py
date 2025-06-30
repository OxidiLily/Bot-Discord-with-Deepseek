# install OpenAI SDK : `pip3 install openai`
import discord
from discord.ext import commands
from openai import OpenAI
import os
from dotenv import load_dotenv

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
    if (message.content == "!tanya halo" or 
        message.content == "!tanya hai" or 
        message.content.startswith("halo") or 
        message.content.startswith('hai')):
        # Kirim pesan balasan ke Discord
        await message.channel.send('🤩 Halo Master 🥰🤭, Saya siap membantu Master 🫡')
        # Menampilkan balasan di terminal
        print(f'[Assistant]: 🤩 Halo Master 🥰🤭, Saya siap membantu Master 🫡')
        return  # Tambahkan return di sini agar tidak memproses command dua kali
    await bot.process_commands(message)
    

@bot.command(name="tanya")
async def tanya(ctx, *, pertanyaan: str):
    """Perintah untuk bertanya kepada DeepSeek."""
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": pertanyaan},
            ],
            stream=False
        )
        # Mengirimkan balasan ke Discord
        await ctx.send(response.choices[0].message.content)
        # Menampilkan balasan di terminal
        print(f'[Assistant]: {response.choices[0].message.content}')
    except Exception as e:
        await ctx.send(f'Terjadi kesalahan saat memproses permintaan 😖😵‍💫😵 ')
        print(f'Error: {str(e)}')

    #print(response.choices[0].message.content)

# Jalankan bot
bot.run(BotDiscord)

