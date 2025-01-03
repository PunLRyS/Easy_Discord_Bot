import discord
from discord.ext import commands

@bot.command(name='join')
async def join(ctx):
    if ctx.author.voice is None:
        await ctx.send("Bạn phải ở trong voice channel để sử dụng lệnh này.")
        return

    voice_channel = ctx.author.voice.channel

    if ctx.voice_client is not None:
        return await ctx.voice_client.move_to(voice_channel)

    voice = await voice_channel.connect()

    # source = discord.FFmpegPCMAudio('D:/test.mp3')
    # voice.play(source)

@bot.command(name='leave')
async def leave(ctx):
    if ctx.voice_client is not None:
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("Bot không ở trong voice channel.")

@bot.command(name='play')
async def play(ctx, file: str , volume: float = 1):
    if ctx.voice_client is None:
        await ctx.send("Bot chưa vào voice channel. Sử dụng lệnh !join để bot vào voice channel trước.")
        return

    if not os.path.isfile(file):
        await ctx.send("File không tồn tại.")
        return

    if not (file.endswith('.mp3') or file.endswith('.wav')):
        await ctx.send("Chỉ hỗ trợ file mp3 hoặc wav.")
        return

    source = discord.FFmpegPCMAudio(file)
    ctx.voice_client.play(source)