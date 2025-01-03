import discord
from discord.ext import commands
from yt_dlp import YoutubeDL
import asyncio
#ADD TOKEN AT BOTTOM OF CODE
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

#global queue for songs
song_queue = []


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

bot.remove_command("help")

@bot.command()
async def help(ctx):
    """Displays a list of all commands and their descriptions."""
    help_message = (
        "**Here are the available commands:**\n"
        "!message: Responds with 'hey whats going on'.\n"
        "!fnaf: Adds and plays 'Five Nights at Freddy's' by The Living Tombstone.\n"
        "!play [search_query]: Searches for and queues the song.\n"
        "!thequeue: Lists all songs in the queue.\n"
        "!skip: Skips the current song.\n"
        "!stop: Stops playback and disconnects the bot.")
    await ctx.send(help_message)


@bot.command()
async def message(ctx):
    """Sends a fixed message."""
    await ctx.send("hey whats going on")


@bot.command()
async def fnaf(ctx):
    """Shortcut to play 'FNAF full song by The Living Tombstone'."""
    #join vc 2x check
    if not ctx.author.voice:
        await ctx.send("You must be in a voice channel to use this command.")
        return

    #join vc
    channel = ctx.author.voice.channel
    if not ctx.voice_client:
        await channel.connect()
    elif ctx.voice_client.channel != channel:
        await ctx.voice_client.move_to(channel)

    #best song ever shortcut
    search_query = "FNAF full song by The Living Tombstone"
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
    }
    async with ctx.typing():
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch:{search_query}", download=False)
                video = info['entries'][0]  #first result always
                audio_url = video['url']
                title = video.get('title', 'Unknown Title')
        except Exception as e:
            await ctx.send(f"Failed to fetch YouTube video: {e}")
            return

    #play music try
    try:
        ctx.voice_client.stop()
        ctx.voice_client.play(
            discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(
                    audio_url,
                    before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
                )
            ),
            after=lambda e: print(f"Finished playing: {e}")
        )
        await ctx.send(f"Now playing: {title}")
    except Exception as e:
        await ctx.send(f"Failed to play {title}: {e}")


@bot.command()
async def play(ctx, *, search_query: str):
    """Searches YouTube and adds the song to the queue."""
    #this searchs YT
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
    }
    async with ctx.typing():
        with YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch:{search_query}",
                                        download=False)
                video = info['entries'][0]  #first result
                url = video['url']
                title = video['title']
            except Exception as e:
                await ctx.send(f"Failed to fetch YouTube video: {e}")
                return

    await add_to_queue(ctx, url, title)


@bot.command()
async def thequeue(ctx):
    """Displays the current song queue."""
    if not song_queue:
        await ctx.send("The queue is empty!")
        return

    queue_list = "\n".join(
        [f"{i+1}. {song['title']}" for i, song in enumerate(song_queue)])
    await ctx.send(f"Current queue:\n{queue_list}")


@bot.command()
async def skip(ctx):
    """Skips the currently playing song."""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop(
        )  #goes to next song in queue
        await ctx.send("Skipped to the next song!")
    else:
        await ctx.send("No song is currently playing.")


async def add_to_queue(ctx, url, title):
    """Adds a song to the queue and starts playback if no song is currently playing."""
    song_queue.append({"url": url, "title": title})
    await ctx.send(f"Added to queue: {title}")

    #play if queue empoty
    if not ctx.voice_client or not ctx.voice_client.is_playing():
        await play_next_song(ctx)


async def play_next_song(ctx):
    """Plays the next song in the queue."""
    if not song_queue:
        await ctx.send("The queue is now empty.")
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        return

    next_song = song_queue.pop(0)
    url = next_song['url']
    title = next_song['title']

    #join user VC
    if not ctx.voice_client:
        channel = ctx.author.voice.channel
        await channel.connect()

    try:
        ctx.voice_client.stop()
        ctx.voice_client.play(discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(url)),
                              after=lambda e: asyncio.run_coroutine_threadsafe(
                                  play_next_song(ctx), bot.loop))
        await ctx.send(f"Now playing: {title}")
    except Exception as e:
        await ctx.send(f"Failed to play {title}: {e}")
        if song_queue:
            await play_next_song(ctx)


@bot.command()
async def stop(ctx):
    """Stops the audio and disconnects from the voice channel."""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel.")
    else:
        await ctx.send("I'm not in a voice channel.")

#to work go to discord developer -> make app -> go to bot -> reset token and copy token inside run
bot.run("")
