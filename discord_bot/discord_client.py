# discord_client.py
from calendar import c
import os
import discord
import tokens
from discord.ext import commands
import youtube_dl
DISCORD_TOKEN = tokens.DISCORD_TOKEN
DISCORD_CHANNEL = tokens.DISCORD_CHANNEL

intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!',intents=intents)

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

#client = discord.Client()
client = commands.Bot(command_prefix='!')

@client.event
async def on_ready():
    print("Bots ready")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!play'):
        if message.channel.id == DISCORD_CHANNEL:
            await  message.channel.send("You'd like to play a song")
            # We want it to join Discord, so we have to have it still connect to commands
            await client.process_commands(message)
        else:
            await message.channel.send("Please post songs in the musicbox, you pleb.")

@client.command()
async def play(ctx, url):
    voice = discord.utils.get(client.voice_clients, guild=ctx.message.guild)

    voice_client = ctx.message.guild.voice_client

    if not ctx.author.voice:
        return await ctx.send("{} is not connected to a voice channel".format(ctx.author.name))
        
    else:
        # Join Voice Channel the author of the message is in

        if voice == None:
            voice_channel = ctx.author.voice.channel
            await voice_channel.connect()

        else:
            voice_channel = ctx.author.voice.channel
            await ctx.send("Getting ready to play in {}".format(voice_channel))
            
        
        #try:
        server = ctx.message.guild
        voice_channel = server.voice_client

        async with ctx.typing():
            filename = await YTDLSource.from_url(url, loop=bot.loop)
            voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=filename))
        await ctx.send("Now Playing: {}".format(filename))
        #except:
        #    await ctx.send("The bot isn't connected to a voice channel...")        
        
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()

@client.command()
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("I'm not in a channel, you weeb..")

if __name__ == "__main__":
    client.run(DISCORD_TOKEN)

