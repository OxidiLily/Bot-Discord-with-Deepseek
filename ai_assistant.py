from message import response_message
import asyncio
from api import AI

async def tanya(ctx, *, tanya: str):
    """Perintah untuk bertanya kepada DeepSeek."""
    try:
        async with ctx.typing():
            loop = asyncio.get_running_loop()
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
        hasil = response.choices[0].message.content
        async with ctx.typing():
            await response_message(hasil, ctx)
    except Exception as e:
        async with ctx.typing():
            await ctx.send(f'Terjadi kesalahan saat memproses permintaan 😖😵‍💫😵 ')
            print(f'Error: {str(e)}')