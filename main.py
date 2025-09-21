# install OpenAI SDK : `pip3 install openai`
import discord
from discord.ext import commands
from message import pesan
from response import tanya, cuaca
import os
import re
from datetime import datetime

# Konfigurasi bot Discord
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents) 
BotDiscord  = os.getenv('BotToken')
today = datetime.now().strftime("%d %B %Y")
logs = re.compile(r"^(?!.*!).+", re.IGNORECASE) # logs yang tidak sesuai dengan perintah !

@bot.event
async def on_ready():
    print(f'Bot {bot.user.name} telah siap!')

@bot.event
async def on_message(message):
    # Menghindari loop tak terbatas
    if message.author == bot.user:
        return
    # Pisahkan antara pesan dari oxidilily dan OxidiLily Assistant#5343
    if str(message.author) == "OxidiLily Assistant#5343":
        print(f'{today} [Assistant]: {message.content}')
    else :
        if logs.match(message.content):  # kalau tidak ada tanda seru di awal
            print(f'{today} [{message.author}]: {message.content}')
        else:
            # Misalnya kalau mau hapus prefix "!" pakai regex
            tanpa_prefix = re.sub(r"^!", "", message.content, count=1)
            # mapping singkatan ke kata lengkap
            mapping = {
                "c": "cuaca",
                "t": "tanya"
            }
            # ganti kalau ada di mapping
            logs_prefix = mapping.get( tanpa_prefix,tanpa_prefix)
            print(f'{today} [{message.author}]: {logs_prefix}')

    # Proses pesan menggunakan fungsi dari message.py
    response = pesan(message)
    if response:
        async with message.channel.typing():
            if isinstance(response, discord.Embed):
                await message.channel.send(embed=response)
                print(f'{today} [Assistant]: {response.title}')
            else:
                await message.channel.send(response)
                print(f'{today} [Assistant]: {response}')   
        return
    await bot.process_commands(message)
    
    
@bot.command(name="tanya", aliases=["t"])
async def handle_tanya(ctx, *, pertanyaan: str=None):
    if pertanyaan is None:
        response_tanya_tidak_sesuai = discord.Embed(
            title="❗ Format Pertanyaan Tidak Sesuai ❗",
            description=f"""
            Master {ctx.author}, tolong masukkan perintah:

            **`!t [sebutkan pertanyaannya]`** atau **`!tanya [sebutkan pertanyaannya]`**
            
            Contoh: **`!t DeepSeek itu apa?`** atau **`!tanya DeepSeek itu apa?`**
            
            mohon sesuai perintahnya yaa...😊🙏
            
            """,
            color=discord.Color.red()
        )
        await ctx.channel.send(embed=response_tanya_tidak_sesuai)
        print(f"{today} [Assistant]: {response_tanya_tidak_sesuai.title}")
        return
    
    await tanya(ctx, tanya=pertanyaan)

@bot.command(name="cuaca", aliases=["c"])
async def handle_cuaca(ctx, *, pertanyaan: str=None):
    if pertanyaan is None:
        response_cuaca_tidak_sesuai = discord.Embed(
            title="❗ Format Cuaca Tidak Sesuai ❗",
            description=f"""
            Master {ctx.author.mention}, tolong masukkan perintah:

            **`!c [sebutkan nama daerahnya]`** atau **`!cuaca [sebutkan nama daerahnya]`**
            
            Contoh: **`!c Jakarta`** atau **`!cuaca Jakarta`**
            
            mohon sesuai perintahnya yaa...😊🙏
            
            """,
            color=discord.Color.red()
        )

        await ctx.channel.send(embed=response_cuaca_tidak_sesuai)
        print(f"{today} [Assistant]: {response_cuaca_tidak_sesuai.title}")
        return

    # Kalau ada input lokasi, panggil fungsi utama
    await cuaca(ctx, cuaca=pertanyaan)

if __name__ == "__main__":
    bot.run(BotDiscord)