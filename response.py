from message import response_message
import asyncio
from openai import OpenAI
import os
from dotenv import load_dotenv
from datetime import datetime

# Mengakses API
load_dotenv()
BotDiscord  = os.getenv('BotToken')
client = OpenAI(api_key=os.getenv('API'), base_url="https://api.deepseek.com")
today = datetime.now().strftime("%A, %d %B %Y")

async def tanya(ctx, *, tanya: str):
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
                        {"role": "user", "content": tanya},
                    ],
                    stream=False
                )
            )
        # Mengambil hasil jawaban dari response API
        hasil = response.choices[0].message.content
        async with ctx.typing():  # Menunjukkan bot sedang mengetik saat memproses hasil
            await asyncio.sleep(3) # Simulasi delay pemrosesan
            # Mengirimkan hasil jawaban ke channel Discord
            await response_message(hasil, ctx)
    except Exception as e:
        async with ctx.typing():
            await asyncio.sleep(1)
        await ctx.send(f'Terjadi kesalahan saat memproses permintaan 😖😵‍💫😵 ')
        print(f'Error: {str(e)}')



async def cuaca(ctx, *, cuaca: str):
    """Perintah untuk bertanya kepada DeepSeek tentang cuaca."""
    try:
        async with ctx.typing():
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": f"tolong carikan informasi cuaca dari {cuaca} berdasarkan data dari BMKG https://www.bmkg.go.id/ dan sumber terpercaya lainnya, berikan informasi yang akurat dan terbaru berdasarkan {today}"},
                        {"role": "user", "content": f"Berikan informasi cuaca terkini di {cuaca}"},
                    ],
                    stream=False
                )
            )
        hasil = response.choices[0].message.content
        async with ctx.typing():
            await asyncio.sleep(3)
            await response_message(hasil, ctx)
    except Exception as e:
        async with ctx.typing():
            await asyncio.sleep(1)
        await ctx.send(f'Terjadi kesalahan saat memproses permintaan 😖😵‍💫😵 ')
        print(f'Error: {str(e)}')