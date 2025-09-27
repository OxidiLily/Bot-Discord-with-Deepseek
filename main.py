# install OpenAI SDK : `pip3 install openai`
import discord
from discord.ext import commands
from message import pesan
from response import tanya, cuaca
import os
import re
from dotenv import load_dotenv
from date import tanggal

# Konfigurasi bot Discord
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents) 

# Mengakses API
load_dotenv()
BotDiscord  = os.getenv('BotToken')

today = tanggal
logs = re.compile(r"^(?!.*!).+", re.IGNORECASE) # logs yang tidak sesuai dengan perintah !
# hilangkan help bawaan supaya tidak bentrok
bot.remove_command("help")

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
            # Pecah input jadi [command, argumen...]
            parts = tanpa_prefix.split(maxsplit=1)
            # mapping singkatan ke kata lengkap
            mapping = {
                "c": "cuaca",
                "t": "tanya",
                "w": "wilayah",  # Tambahan untuk pencarian wilayah
            }
            # Ambil logs_prefix dan argumen
            logs_prefix= parts[0].lower()
            argumen = parts[1] if len(parts) > 1 else ""
            # ganti kalau ada di mapping
            logs_prefix = mapping.get( logs_prefix, logs_prefix)
            # Gabungkan lagi command + argumen
            final_logs = f"{logs_prefix} {argumen}".strip()
            print(f'{today} [{message.author}]: {final_logs}')

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
            title="❌ Format Pertanyaan Tidak Sesuai ❌",
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
            title="❌ Format Cuaca Tidak Sesuai ❌",
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
    await cuaca(ctx, daerah=pertanyaan)

@bot.command(name="wilayah", aliases=["w"])
async def handle_wilayah(ctx, *, nama: str=None):
    """Command untuk mencari wilayah dalam database"""
    if nama is None:
        response_wilayah_tidak_sesuai = discord.Embed(
            title="❌ Format Pencarian Wilayah Tidak Sesuai ❌",
            description=f"""
            Master {ctx.author.mention}, tolong masukkan perintah:

            **`!w [nama wilayah yang dicari]`** atau **`!wilayah [nama wilayah yang dicari]`**
            
            Contoh: **`!w Jakarta`** atau **`!wilayah Bandung`**
            
            Command ini berguna untuk mencari dan melihat semua wilayah yang tersedia dalam database.
            
            """,
            color=discord.Color.red()
        )

        await ctx.channel.send(embed=response_wilayah_tidak_sesuai)
        print(f"{today} [Assistant]: {response_wilayah_tidak_sesuai.title}")
        return

    # Import fungsi pencarian wilayah dari response
    from response import load_wilayah_data, wilayah_cache
    
    async with ctx.typing():
        await load_wilayah_data()
        
        if not wilayah_cache:
            embed = discord.Embed(
                title="❌ Error Database",
                description="Tidak dapat mengakses database wilayah. Coba lagi nanti.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        nama_lower = nama.lower().strip()
        hasil = []
        
        # Cari wilayah yang cocok
        for kode, wilayah in wilayah_cache:
            if nama_lower in wilayah.lower():
                hasil.append((kode, wilayah))
                if len(hasil) >= 15:  # Batasi hasil maksimal 15
                    break
        
        if not hasil:
            embed = discord.Embed(
                title="❌ Wilayah Tidak Ditemukan",
                description=f"Tidak ada wilayah yang cocok dengan '{nama}'",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        description = f"Hasil pencarian untuk '{nama}':\n\n"
        
        for i, (kode, wilayah) in enumerate(hasil, 1):
            description += f"**{i}.** {wilayah}\n   └─ Kode: `{kode}`\n\n"
        
        # Batasi panjang description untuk Discord
        if len(description) > 4000:
            description = description[:3900] + "\n\n*... dan lainnya*"
        
        embed = discord.Embed(
            title="🔍 Hasil Pencarian Wilayah",
            description=description,
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Ditemukan {len(hasil)} wilayah")
        
        await ctx.send(embed=embed)

@bot.command(name="help", aliases=["h"])
async def help_command(ctx):
    """Command help yang diperbaiki"""
    embed = discord.Embed(
        title="🤖 Bantuan Bot Assistant",
        description="Berikut adalah daftar perintah yang tersedia:",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="💬 Tanya AI",
        value="**`!t [pertanyaan]`** atau **`!tanya [pertanyaan]`**\nBertanya kepada AI DeepSeek",
        inline=False
    )
    
    embed.add_field(
        name="🌤️ Cuaca",
        value="**`!c [nama daerah]`** atau **`!cuaca [nama daerah]`**\nCek prakiraan cuaca dari BMKG",
        inline=False
    )
    
    embed.add_field(
        name="🔍 Cari Wilayah",
        value="**`!w [nama wilayah]`** atau **`!wilayah [nama wilayah]`**\nCari wilayah yang tersedia dalam database",
        inline=False
    )
    
    embed.add_field(
        name="💡 Tips",
        value="• Gunakan `!w Jakarta` untuk melihat semua wilayah Jakarta\n• Coba nama yang lebih spesifik jika cuaca tidak ditemukan\n• Contoh: `!c Jakarta Utara`, `!c Bandung`",
        inline=False
    )
    
    embed.set_footer(text="Gunakan perintah sesuai format untuk hasil terbaik!")
    
    await ctx.send(embed=embed)

if __name__ == "__main__":
    bot.run(BotDiscord)