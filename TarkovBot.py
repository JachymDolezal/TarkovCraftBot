import discord
from config_bot import TOKEN
from discord.ext import commands
import pandas as pd
import os
from discord.ext import commands,tasks
import youtube_dl
import asyncio
pd.options.mode.chained_assignment = None

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='!',intents=intents)
client = discord.Client(intents=intents)
station_keyword = ['Workbench', 'Medstation', 'Nutrition', 'Lavatory']


# command to clear channel messages
@bot.command(name='clear')
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount)
    await ctx.send("Messages have been cleared")


# # test embed command
# @bot.command(name='test')
# async def test(ctx, arg):
#
#     name = str(ctx.guild.owner)
#     embed = discord.Embed(
#         title=ctx.guild.name + " Server Information",
#     )
#     embed.add_field(name="Owner", value=name, inline=True)
#     embed.add_field(name="message", value=arg, inline=True)
#
#     await ctx.send(embed=embed)


# command for showing tarkov crafts.
@bot.command(name='crafts', help=f"args:{','.join(station_keyword)}")
async def give_stats(ctx, arg):
    # sorts the data by profit per hour index
    df = pd.read_csv("Data/TarkovData.csv")
    df = df[df['profit_per_hour'] > 0]
    if arg == 'help':
        await ctx.send(f"use this command with following argument: {','.join(station_keyword)}")
    elif arg in station_keyword:
        if arg == 'Nutrition':
            arg = 'Nutrition unit'
        # prints all data from all 3 of a given station
        new_df = df.loc[df['station'].str.contains(arg)]
        new_df.drop(['station', 'duration'], axis=1, inplace=True)
        if not new_df.empty:
            new_df = new_df.sort_values(by=['profit_per_hour'], ascending=False)
            embed = discord.Embed(
                title=f"Crafts in {arg} sorted by profit per hour in roubles",
            )
            embed.add_field(name="Name", value=new_df.name.to_string(index=False), inline=True)
            embed.add_field(name="Profit_per_hour", value=new_df.profit_per_hour.to_string(index=False),inline=True)
            embed.add_field(name="Profit", value=new_df.profit.to_string(index=False), inline=True)

            await ctx.send(embed=embed)
    elif arg == 'all':
        await ctx.send(f"**Top crafts by profit per hour**")
        # outputs top 10 columns sorted by profit_per_hour
        df.drop(['station', 'output_price', 'input_price', 'duration'], axis=1, inplace=True)
        df = df.sort_values(by=['profit_per_hour'], ascending=False)
        df = df.iloc[:10, :]
        embed = discord.Embed(
            title=f"Top 10 crafts with positive profit per hour in roubles",
        )
        embed.add_field(name="Name", value=df.name.to_string(index=False), inline=True)
        embed.add_field(name="Profit_per_hour", value=df.profit_per_hour.to_string(index=False), inline=True)
        embed.add_field(name="Profit", value=df.profit.to_string(index=False), inline=True)

        await ctx.send(embed=embed)
    else:
        await ctx.send("wrong command argument, use !TarkovStats help to see available arguments")

youtube_dl.utils.bug_reports_message = lambda: ''
ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}
ffmpeg_options = {
    'options': '-vn'
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""
    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename


@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()


@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")


@bot.command(name='play', help='To play song')
async def play(ctx, url):
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client
        async with ctx.typing():
            filename = await YTDLSource.from_url(url, loop=bot.loop)
            voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=filename))
        await ctx.send('**Now playing:** {}'.format(filename))
    except:
        await ctx.send("The bot is not connected to a voice channel.")


@bot.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("The bot is not playing anything at the moment.")


@bot.command(name='resume', help='Resumes the song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send("The bot was not playing anything before this. Use play_song command")


@bot.command(name='stop', help='Stops the song')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything at the moment.")


bot.run(TOKEN)
