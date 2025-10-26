import asyncio
from ai_assistant import tanya
from cuaca import cuaca # Import here to avoid circular dependency


async def tanya_command(ctx, *, query: str):
    # Call the imported `tanya` from ai_assistant; handle both coroutine and regular function return values.
    try:
        result = tanya(ctx, tanya=query)
        if asyncio.iscoroutine(result):
            await result
    except Exception as e:
        # If the imported function raises, print for debugging but don't crash the caller.
        print(f"Error calling ai_assistant.tanya: {e}")

async def weather_command(ctx, *, location: str):
    try:
        weather_info = await cuaca(ctx, daerah=location)
        if weather_info:
            await ctx.send(weather_info)
        else:
            await ctx.send(f"Maaf, informasi cuaca untuk lokasi '{location}' tidak ditemukan.")
    except Exception as e:
        print(f"Error fetching weather info: {e}")
        await ctx.send("Terjadi kesalahan saat mengambil informasi cuaca.")