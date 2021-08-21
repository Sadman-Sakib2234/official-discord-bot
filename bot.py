import asyncio
import os
import random
import time
from io import BytesIO
from itertools import cycle

import animec
import discord
import giphy_client
import requests
from discord.ext import commands, tasks
from discord_slash import SlashCommand
from dotenv import load_dotenv
from giphy_client.rest import ApiException
from PIL import Image, ImageDraw, ImageFont

import levelsys
import poll

# getting token from .env file

load_dotenv()

TOKEN = os.getenv('TOKEN')

# intents
intents = discord.Intents().all()
client = commands.Bot(command_prefix=">", intents=intents)
intents.members = True
# removing builtin help command
client.remove_command("help")

# slash command
slash = SlashCommand(client, sync_commands=True)

# cogs

cogs = [levelsys, poll]

player1 = ""
player2 = ""
turn = ""
gameOver = True

board = []



winningConditions = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6]
]

snipe_message_author = {}
snipe_message_content = {}

filter_words = ["nigga", "creampie", "pussy"]


# member join embed

@client.event
async def on_member_join(member):
    wellcomeEmbed = discord.Embed(title=f"Hello, {member.name} Wellcome to the server",
                                  description=f"{member.name} thanks for joining the server.<#860751345056481310> to read the rule and <#860760167963295765> to get a role thank you. we hope you like the server and have a great day.", color=discord.Color.dark_purple())
    wellcomeEmbed.set_author(name=member.name, icon_url=member.avatar_url)
    await client.get_channel(860731320988073994).send(embed=wellcomeEmbed)

# bot is ready and changing status

# all status

status = cycle([
    'You',
    "you call it main bot or MainBot both are stupid"
    'the world burn',
    "main bot. wait what...",
    "main bot suffer",
    "main bot's code hmmmm",
    'Kids suffer',
])


@tasks.loop(seconds=60)
async def status_swap():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=next(status)))


@client.event
async def on_ready():
    status_swap.start()
    print("Bot Ready...")


@client.event
async def on_message(msg):
    for word in filter_words:
        if word in msg.content:
            await msg.delete()

@client.event
async def on_message_delete(message):
    snipe_message_author[message.channel.id] = message.author
    snipe_message_content[message.channel.id] = message.content
    await asyncio.sleep(60)
    del snipe_message_author[message.channel.id]
    del snipe_message_content[message.channel.id]


@client.command()
async def snipe(ctx):
    channel = ctx.channel
    try:
        snipeEmbed = discord.Embed(
            title=f"Snipe in {channel.name}", description=snipe_message_content[channel.id], color=discord.Color.dark_purple())
        snipeEmbed.set_footer(
            text=f"Deleted by {snipe_message_author[channel.id]}")
        await ctx.send(embed=snipeEmbed)
    except:
        await ctx.send("Nothing to snipe")
# help command


@client.command()
async def help(ctx):
    helpEmbed = discord.Embed(title="Help", color=discord.Color.dark_purple())
    helpEmbed.add_field(name="Moderation Commands",
                        value="`ban`, `kick`, `mute`, `unmute`, `unban`, `clear`, `poll`, `snipe`", inline=False)
    helpEmbed.add_field(name="Fun Commands", value="`wanted`, `ping`, `avatar`, `meme`, `cringe`, `timer`, `animeme`, `shit`, `emojify`, `babysay`, `gif`, `tweet`, `snek`, `puppy`, `joke`, `tictactoe & place`, `rip`, `slap`, `covid`, `brazzers`, `anime`, `animecharacters`", inline=False)
    helpEmbed.add_field(name="Rank commands",
                        value="`rank`, `leaderboard`", inline=False)
    helpEmbed.add_field(name="Other commands",
                        value="`snipe`, `credits`, `realcredits`", inline=False)
    await ctx.send(embed=helpEmbed)


# ping command similar to test command

@commands.cooldown(1, 15, commands.BucketType.user)
@client.command(aliases=["test"])
async def ping(ctx):
    await ctx.send(f'Bot Speed - {round(client.latency * 1000)}ms')


@ping.error
async def ping_error(error, ctx):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send('This command is on cooldown, you can use it in {round(error.retry_after, 2)}')

# Wanted command show pic of avatar on wanted poster


@commands.cooldown(1, 15, commands.BucketType.user)
@client.command()
async def wanted(ctx, member: discord.Member = None):
    if member == None:
        member = ctx.author

    wanted = Image.open("./images/wanted.jpg")

    asset = member.avatar_url_as(size=128)
    data = BytesIO(await asset.read())
    profiepic = Image.open(data)

    profiepic = profiepic.resize((290, 290))

    wanted.paste(profiepic, (87, 224))

    wanted.save("wantedpic.jpg")

    await ctx.send(file=discord.File("wantedpic.jpg"))

    os.remove("wantedpic.jpg")


@wanted.error
async def wanted_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send('This command is on cooldown, you can use it in {round(error.retry_after, 2)}')

# I stepped on shit meme generator


@commands.cooldown(1, 15, commands.BucketType.user)
@client.command()
async def shit(ctx, member: discord.Member = None):
    if member == None:
        member = ctx.author

    wanted = Image.open("./images/shit.png")

    asset = member.avatar_url_as(size=128)
    data = BytesIO(await asset.read())
    profiepic = Image.open(data)

    profiepic = profiepic.resize((200, 200))

    wanted.paste(profiepic, (230, 747))

    wanted.save("shitpic.png")

    await ctx.send(file=discord.File("shitpic.png"))

    os.remove("shitpic.png")


@shit.error
async def shit_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send('This command is on cooldown, you can use it in {round(error.retry_after, 2)}')

# covid command


@client.command()
async def covid(ctx, *, countryName=None):
    try:
        if countryName is None:
            embed = discord.Embed(title="This command is used like this: ```!covid [country]```", colour=discord.Color.dark_purple(
            ), timestamp=ctx.message.created_at)
            await ctx.send(embed=embed)

        else:
            url = f"https://coronavirus-19-api.herokuapp.com/countries/{countryName}"
            stats = requests.get(url)
            json_stats = stats.json()
            country = json_stats["country"]
            totalCases = json_stats["cases"]
            todayCases = json_stats["todayCases"]
            totalDeaths = json_stats["deaths"]
            todayDeaths = json_stats["todayDeaths"]
            recovered = json_stats["recovered"]
            active = json_stats["active"]
            critical = json_stats["critical"]
            casesPerOneMillion = json_stats["casesPerOneMillion"]
            deathsPerOneMillion = json_stats["deathsPerOneMillion"]
            totalTests = json_stats["totalTests"]
            testsPerOneMillion = json_stats["testsPerOneMillion"]

            embed2 = discord.Embed(title=f"**COVID-19 Status Of {country}**!", description="This Information Isn't Live Always, Hence It May Not Be Accurate!",
                                   colour=discord.Color.dark_purple(), timestamp=ctx.message.created_at)
            embed2.add_field(name="**Total Cases**",
                             value=totalCases, inline=True)
            embed2.add_field(name="**Today Cases**",
                             value=todayCases, inline=True)
            embed2.add_field(name="**Total Deaths**",
                             value=totalDeaths, inline=True)
            embed2.add_field(name="**Today Deaths**",
                             value=todayDeaths, inline=True)
            embed2.add_field(name="**Recovered**",
                             value=recovered, inline=True)
            embed2.add_field(name="**Active**", value=active, inline=True)
            embed2.add_field(name="**Critical**", value=critical, inline=True)
            embed2.add_field(name="**Cases Per One Million**",
                             value=casesPerOneMillion, inline=True)
            embed2.add_field(name="**Deaths Per One Million**",
                             value=deathsPerOneMillion, inline=True)
            embed2.add_field(name="**Total Tests**",
                             value=totalTests, inline=True)
            embed2.add_field(name="**Tests Per One Million**",
                             value=testsPerOneMillion, inline=True)

            embed2.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/564520348821749766/701422183217365052/2Q.png")
            await ctx.send(embed=embed2)

    except:
        embed3 = discord.Embed(title="Invalid Country Name Or API Error! Try Again..!",
                               colour=discord.Color.dark_purple(), timestamp=ctx.message.created_at)
        embed3.set_author(name="Error!")
        await ctx.send(embed=embed3)


# rip command :(


@client.command()
async def rip(ctx, member: discord.Member = None):
    if member == None:
        member = ctx.author

    dead = Image.open("./images/grave.png")

    asset = member.avatar_url_as(size=128)
    data = BytesIO(await asset.read())
    profiepic = Image.open(data)

    profiepic = profiepic.resize((210, 210))

    dead.paste(profiepic, (92, 235))

    dead.save("dead.png")

    await ctx.send(file=discord.File("dead.png"))

    os.remove("dead.png")


@rip.error
async def rip_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You have to give a member to kill.")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("Please include a valid member | member not found")

# slap command


@client.command()
async def slap(ctx, member: discord.Member = None):
    if member == None:
        ctx.send("Include a member to slap")

    slap = Image.open("./images/slap.jpg")

    asset = member.avatar_url_as(size=128)
    data = BytesIO(await asset.read())
    profiepic = Image.open(data)
    profiepic = profiepic.resize((300, 300))

    slap.paste(profiepic, (833, 339))

    assettwo = ctx.author.avatar_url_as(size=128)
    data = BytesIO(await assettwo.read())
    profiepictwo = Image.open(data)
    profiepictwo = profiepictwo.resize((300, 300))

    slap.paste(profiepictwo, (475, 85))

    slap.save("slap.jpg")

    await ctx.send(file=discord.File("slap.jpg"))

    os.remove("slap.jpg")


# brazzers commands

@client.command()
async def brazzers(ctx, member: discord.Member = None):
    if member == None:
        member = ctx.author

    logo = Image.open("./images/brazzers.png")

    asset = member.avatar_url_as(size=128)
    data = BytesIO(await asset.read())
    profiepic = Image.open(data)

    logo = logo.resize((200, 40))
    profiepic = profiepic.resize((300, 300))

    profiepic.paste(logo, (89, 249))

    profiepic.save("profiepic.png")

    await ctx.send(file=discord.File("profiepic.png"))

    os.remove("profiepic.png")

# simp rate command copy from horizon bot


@client.command()
async def simprate(ctx):
    randomnumber = random.randint(1, 100)
    await ctx.send(f'your simp rate is, {randomnumber}%')

# baby first word meme


@client.command()
async def babysay(ctx, *, text="No text"):
    babypic = Image.open("./images/baby.png")

    babydraw = ImageDraw.Draw(babypic)
    font = ImageFont.truetype("./fonts/dkfont.otf", 24)

    babydraw.text((54, 313), text, (0, 0, 0), font=font)

    babypic.save("babysays.png")

    await ctx.send(file=discord.File("babysays.png"))

    os.remove("babysays.png")


@babysay.error
async def babysay_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You have to write something to make the baby say")

# trump tweet meme


@client.command()
async def tweet(ctx, *, text="No text"):
    tweetpic = Image.open("./images/trump.jpg")

    trumdraw = ImageDraw.Draw(tweetpic)
    tweetfont = ImageFont.truetype("./fonts/tommy.otf", 30)

    trumdraw.text((9, 81), text, (0, 0, 0), font=tweetfont)

    tweetpic.save("trumpsays.jpg")

    await ctx.send(file=discord.File("trumpsays.jpg"))

    os.remove("trumpsays.jpg")


@tweet.error
async def tweet_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You have to write something to tweet")

# facts tweet meme


@client.command()
async def facts(ctx, *, text="No text"):
    fatxpic = Image.open("./images/factz.jpg")

    factdraw = ImageDraw.Draw(fatxpic)
    tweetfont = ImageFont.truetype("./fonts/tommy.otf", 20)

    factdraw.text((46, 362), text, (0, 0, 0), font=tweetfont)

    fatxpic.save("facts.jpg")

    await ctx.send(file=discord.File("facts.jpg"))

    os.remove("facts.jpg")


@facts.error
async def facts_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You have to write something to tweet")

# dank memer emojify command


@commands.cooldown(1, 5, commands.BucketType.user)
@client.command()
async def emojify(ctx, *, text):
    emojis = []

    for s in text:
        if s.isdecimal():
            num2emo = {
                '0': 'zero',
                '1': 'one',
                '2': 'two',
                '3': 'three',
                '4': 'four',
                '5': 'five',
                '6': 'six',
                '7': 'seven',
                '8': 'eight',
                '9': 'nine'
            }
            emojis.append(f': {num2emo.get(s)}')
        elif s.isalpha():
            emojis.append(f' :regional_indicator_{s}: ')
        else:
            emojis.append(s)
    await ctx.send(''.join(emojis))
# Avatar command


@commands.cooldown(1, 15, commands.BucketType.user)
@client.command()
async def avatar(ctx, member: discord.Member = None):
    if member == None:
        member = ctx.author

    memberAvatar = member.avatar_url

    avatarEmbed = discord.Embed(title=f"{member.name}'s avatar")
    avatarEmbed.set_image(url=memberAvatar)

    await ctx.send(embed=avatarEmbed)


@client.command()
async def meme(ctx):
    r = requests.get("https://memes.blademaker.tv/api/meme")
    res = r.json()

    title = res["title"]
    ups = res["ups"]
    downs = res["downs"]

    memeEmbed = discord.Embed(title=f"{title}\n")
    memeEmbed.set_image(url=res["image"])
    memeEmbed.set_footer(text=f"👍: {ups} 👎: {downs}")

    await ctx.send(embed=memeEmbed)


@client.command()
async def cringe(ctx):
    r = requests.get("https://memes.blademaker.tv/api/cringepics")
    res = r.json()

    title = res["title"]
    ups = res["ups"]
    downs = res["downs"]

    cringememeEmbed = discord.Embed(title=f"{title}\n")
    cringememeEmbed.set_image(url=res["image"])
    cringememeEmbed.set_footer(text=f"👍: {ups} 👎: {downs}")

    await ctx.send(embed=cringememeEmbed)

# anime meme


@client.command()
async def animeme(ctx):
    r = requests.get("https://memes.blademaker.tv/api/AnimeFunny")
    res = r.json()

    title = res["title"]
    ups = res["ups"]
    downs = res["downs"]

    cringememeEmbed = discord.Embed(title=f"{title}\n")
    cringememeEmbed.set_image(url=res["image"])
    cringememeEmbed.set_footer(text=f"👍: {ups} 👎: {downs}")

    await ctx.send(embed=cringememeEmbed)

# anime comman


@client.command()
async def anime(ctx, *, query):
    try:
        anime = animec.Anime(query)
    except:
        animeerrorEmbed = discord.Embed(
            description="No anime found with the name in search", color=discord.Color.dark_purple())
        await ctx.send(embed=animeerrorEmbed)
        return

    animeEmbed = discord.Embed(title=f"{anime.title_english}({anime.title_jp})",
                               description=f"{anime.description[:200]}...", color=discord.Color.dark_purple())
    animeEmbed.add_field(name="Episode Count:", value=str(anime.episodes))
    animeEmbed.add_field(name="Rating:", value=str(anime.rating))
    animeEmbed.add_field(name="Popularity:", value=str(anime.popularity))
    animeEmbed.add_field(name="Genres:", value=str(anime.genres))
    animeEmbed.add_field(name="Status:", value=str(anime.status))
    animeEmbed.add_field(name="NSFW Status:", value=str(anime.is_nsfw()))
    animeEmbed.set_image(url=anime.poster)

    await ctx.send(embed=animeEmbed)


@client.command(aliases=["char", 'animechar', 'charsearch'])
async def animecharacters(ctx, *, query):
    try:
        char = animec.Charsearch(query)
    except:
        print("error")
        animeerrorEmbed = discord.Embed(
            description="No anime characters found with the name in search", color=discord.Color.dark_purple())
        await ctx.send(embed=animeerrorEmbed)
        return

    animecharEmbed = discord.Embed(
        title=f"{char.title}", url=char.url, color=discord.Color.dark_purple())
    animecharEmbed.set_image(url=char.image_url)
    animecharEmbed.set_footer(text=", ".join(list(char.references.keys())[:2]))

    await ctx.send(embed=animecharEmbed)


@animecharacters.error
async def animecharacters_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please include a anime character name.")

# snek picture


@client.command()
async def snek(ctx):
    r = requests.get("https://memes.blademaker.tv/api/Snek")
    res = r.json()

    title = res["title"]

    cringememeEmbed = discord.Embed(title=f"{title}\n")
    cringememeEmbed.set_image(url=res["image"])
    cringememeEmbed.set_footer(text="snek go brrrr")

    await ctx.send(embed=cringememeEmbed)

# cute doggo


@client.command()
async def puppy(ctx):
    r = requests.get("https://memes.blademaker.tv/api/PuppySmiles")
    res = r.json()

    title = res["title"]

    cringememeEmbed = discord.Embed(title=f"{title}\n")
    cringememeEmbed.set_image(url=res["image"])
    cringememeEmbed.set_footer(text="cute doggos")

    await ctx.send(embed=cringememeEmbed)

#  dad joke


@client.command()
async def joke(ctx):
    r = requests.get("https://v2.jokeapi.dev/joke/Any?type=single")
    res = r.json()

    title = res["joke"]
    category = res["category"]

    jokeEmbed = discord.Embed(title=f"{title}\n")
    jokeEmbed.set_footer(text=f"category: {category}")

    await ctx.send(embed=jokeEmbed)


# giphy command api or smh

@client.command()
async def gif(ctx, *, q="random"):

    api_key = "BesVBWQ7n9BO2L7WaQLRIitxFbeFTKUq"
    api_instance = giphy_client.DefaultApi()

    try:
        # Search Endpoint

        api_response = api_instance.gifs_search_get(
            api_key, q, limit=5, rating='g')
        lst = list(api_response.data)
        giff = random.choice(lst)

        emb = discord.Embed(title=f'{q} gif')
        emb.set_image(url=f'https://media.giphy.com/media/{giff.id}/giphy.gif')

        await ctx.channel.send(embed=emb)
    except ApiException as e:
        print("Exception when calling DefaultApi->gifs_search_get: %s\n" % e)


@client.command()
async def timer(ctx, seconds):
    try:
        secondint = int(seconds)
        if secondint > 300:
            await ctx.send("You cant go over 5 mins idiot.")
            raise BaseException
        elif secondint <= 0:
            await ctx.send("Are you an alien why are you setting timer to negative is this a new thing...")
            raise BaseException

        message = await ctx.send(f"Timer: {seconds}")

        while True:
            secondint -= 1
            if secondint == 0:
                await message.edit(content="Timer Ended")
                break

            await message.edit(content=f"Timer: {secondint}")
        await ctx.send(f"{ctx.author.mention}, your Time has been ended!")
    except ValueError:
        await ctx.send("You need to enter a number dickhead")
# kick command similar to boot


@client.command(aliases=["boot"])
async def kick(ctx, member: discord.Member, *, reason=None):
    if (not ctx.author.guild_permissions.kick_members):
        await ctx.send("This command requires `Kick Members` permission dickhead.")
        return
    await member.kick(reason=reason)
    await ctx.send(f'{member.mention} has been kicked.')

# kick command error handling


@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please include a member")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("Please include a valid member | member not found")

# ban command similar to hammer


@client.command(aliases=["hammer"])
async def ban(ctx, member: discord.Member, *, reason=None):
    if (not ctx.author.guild_permissions.ban_members):
        await ctx.send("This command requires `Ban Members` permission dickhead.")
        return
    await member.ban(reason=reason)
    await ctx.send(f'{member.mention} has been banned.')

# ban command error handling


@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please include a member")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("Please include a valid member | member not found")

# unban comman similar to forgiveness


@client.command(aliases=['forgive'])
async def unban(ctx, *, member):
    if (not ctx.author.guild_permissions.ban_members):
        await ctx.send("This command requires `Ban Member` permission dickhead.")
        return
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user
        if(user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'{member.mention} has been unbanned.')
            return

# clear command to clear previous messages


@client.command(aliases=['purge'])
async def clear(ctx, amount=11):
    if (not ctx.author.guild_permissions.manage_messages):
        await ctx.send("This command requires `Manage Messages` permission dickhead.")
        return
    amount = amount + 1
    if amount > 200:
        await ctx.send("Cant delete more than 100 messages.")
    else:
        await ctx.channel.purge(limit=amount)
        await ctx.send("Cleared Messages.")

# mute command


@client.command()
async def mute(ctx, member: discord.Member, *, reason=None):
    if (not ctx.author.guild_permissions.manage_messages):
        await ctx.send("This command requires `Mute Member` permission dickhead.")
        return
    guild = ctx.guild
    mutedRole = discord.utils.get(guild.roles, name="Muted")

    if not mutedRole:
        await ctx.send("No mute role found. creating a mute role....")
        mutedRole = await guild.create_role(name="Muted")

        for channel in guild.channels:
            await ctx.send("No mute role found, Creating a role....")
            await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=False, read_messages=True)
    await member.add_roles(mutedRole, reason=reason)
    await ctx.send("User muted.")
    await member.send(f"You have been muted from **{guild.name}** | Reason: **{reason}**")

# mute command error handling


@mute.error
async def mute_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please include a member")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("Please include a valid member | member not found")

# unmute command


@client.command()
async def unmute(ctx, member: discord.Member, *, reason=None):
    if (not ctx.author.guild_permissions.manage_messages):
        await ctx.send("This command requires `Manage Messages` permission dickhead.")
        return
    guild = ctx.guild
    mutedRole = discord.utils.get(guild.roles, name="Muted")

    if not mutedRole:
        await ctx.send("The muted role has not benn found. If you dont have muted role please run `v!mutedrole create` or name your current role to `Muted`.")
        return

    await member.remove_roles(mutedRole, reason=reason)
    await ctx.send("User unmuted.")
    await member.send(f"You have been unmuted from **{guild.name}**")

# mute command error handling


@unmute.error
async def unmute_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please include a member")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("Please include a valid member | member not found")

# Slow mode command


@client.command()
async def slowmode(ctx, time: int):
    if (not ctx.author.guild_permissions.manage_messages):
        await ctx.send("This command requires `Manage Messages` permission dickhead.")
        return
    try:
        if time == 0:
            await ctx.send("Slowmode Off.")
            await ctx.channel.edit(slowmode_delay=0)
        elif time > 21600:
            await ctx.send('You cant set slowmode above 6 hours dickhead.')
            return
        else:
            await ctx.channel.edit(slowmode_delay=time)
            await ctx.send(f'Slowmode set to {time} seconds!')

    except Exception:
        await print("OOPS idk")


# server info command
@commands.cooldown(1, 15, commands.BucketType.user)
@client.command()
async def serverinfo(ctx):
    role_count = len(ctx.guild.roles)
    list_of_bots = [bot.mention for bot in ctx.guild.members if bot.bot]

    serverinfoEmbed = discord.Embed(
        timestamp=ctx.message.created_at, color=discord.Color.dark_purple())
    serverinfoEmbed.add_field(
        name="Name", value=f"{ctx.guild.name}", inline=True)
    serverinfoEmbed.add_field(
        name="Member Count", value=ctx.guild.member_count, inline=True)
    serverinfoEmbed.add_field(
        name="Bots:", value=', '.join(list_of_bots), inline=True)
    serverinfoEmbed.add_field(
        name='Highest role', value=ctx.guild.roles[-9], inline=True)
    serverinfoEmbed.add_field(
        name="Total Roles", value=str(role_count), inline=True)
    serverinfoEmbed.add_field(name='Created At', value=ctx.guild.created_at.__format__(
        '%A, %d. %B %Y @ %H:%M:%S'), inline=True)
    serverinfoEmbed.set_thumbnail(url=ctx.guild.icon_url)
    serverinfoEmbed.set_footer(
        text=ctx.bot.user.name, icon_url=ctx.bot.user.avatar_url)
    await ctx.send(embed=serverinfoEmbed)


@serverinfo.error
async def serverinfo_error(error, ctx):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f'This command is on cooldown, you can use it in {round(error.retry_after, 2)}')

# Slash Commands


@slash.slash(description="Shows bots latency")
async def ping(ctx):
    await ctx.send(f'Bot Speed - {round(client.latency * 1000)}ms')


@slash.slash(description="Generates a random number")
async def randomnumber(ctx):
    randomnumber = random.randint(1, 999999999)
    await ctx.send(f'Number: {randomnumber}')


@slash.slash(description="how much a simp are you")
async def simprate(ctx):
    randomnumber = random.randint(1, 100)
    await ctx.send(f'your simp rate is, {randomnumber}%')

# Games

# tic tac toe


@client.command()
async def tictactoe(ctx, p1: discord.Member, p2: discord.Member):
    global count
    global player1
    global player2
    global turn
    global gameOver

    if gameOver:
        global board
        board = [":white_large_square:", ":white_large_square:", ":white_large_square:",
                 ":white_large_square:", ":white_large_square:", ":white_large_square:",
                 ":white_large_square:", ":white_large_square:", ":white_large_square:"]
        turn = ""
        gameOver = False
        count = 0

        player1 = p1
        player2 = p2

        # print the board
        line = ""
        for x in range(len(board)):
            if x == 2 or x == 5 or x == 8:
                line += " " + board[x]
                await ctx.send(line)
                line = ""
            else:
                line += " " + board[x]

        # determine who goes first
        num = random.randint(1, 2)
        if num == 1:
            turn = player1
            await ctx.send("It is <@" + str(player1.id) + ">'s turn.")
        elif num == 2:
            turn = player2
            await ctx.send("It is <@" + str(player2.id) + ">'s turn.")
    else:
        await ctx.send("A game is already in progress! Finish it before starting a new one.")


@client.command()
async def place(ctx, pos: int):
    global turn
    global player1
    global player2
    global board
    global count
    global gameOver

    if not gameOver:
        mark = ""
        if turn == ctx.author:
            if turn == player1:
                mark = ":regional_indicator_x:"
            elif turn == player2:
                mark = ":o2:"
            if 0 < pos < 10 and board[pos - 1] == ":white_large_square:":
                board[pos - 1] = mark
                count += 1

                # print the board
                line = ""
                for x in range(len(board)):
                    if x == 2 or x == 5 or x == 8:
                        line += " " + board[x]
                        await ctx.send(line)
                        line = ""
                    else:
                        line += " " + board[x]

                checkWinner(winningConditions, mark)
                print(count)
                if gameOver == True:
                    await ctx.send(mark + " wins!")
                elif count >= 9:
                    gameOver = True
                    await ctx.send("It's a tie!")

                # switch turns
                if turn == player1:
                    turn = player2
                elif turn == player2:
                    turn = player1
            else:
                await ctx.send("Be sure to choose an integer between 1 and 9 (inclusive) and an unmarked tile.")
        else:
            await ctx.send("It is not your turn.")
    else:
        await ctx.send("Please start a new game using the !tictactoe command.")


def checkWinner(winningConditions, mark):
    global gameOver
    for condition in winningConditions:
        if board[condition[0]] == mark and board[condition[1]] == mark and board[condition[2]] == mark:
            gameOver = True


@tictactoe.error
async def tictactoe_error(ctx, error):
    print(error)
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please mention 2 players for this command.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Please make sure to mention/ping players (ie. <@688534433879556134>).")


@place.error
async def place_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please enter a position you would like to mark.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Please make sure to enter an integer.")

# eightball


@client.command(aliases=['eightball', '8ball', '8b'])
async def _8ball(ctx, *, question):
    responses = [
        'Hell no.',
        'Prolly not.',
        'Idk bro.',
        'Prolly.',
        'Hell yeah my dude.',
        'It is certain.',
        'It is decidedly so.',
        'Without a Doubt.',
        'Yes - Definitaly.',
        'You may rely on it.',
        'As i see it, Yes.',
        'Most Likely.',
        'Outlook Good.',
        'Yes!',
        'No!',
        'Signs a point to Yes!',
        'Reply Hazy, Try again.',
        'IDK but u should subscribe to darkviper and lsg gaming.',
        'Better not tell you know.',
        'Cannot predict now.',
        'Concentrate and ask again.',
        "Don't Count on it.",
        'My reply is No.',
        'My sources say No.',
        'Outlook not so good.',
        'Very Doubtful']

    await ctx.send(f':8ball: Question: {question}\n :8ball: {random.choice(responses)}')


@place.error
async def _8bal_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please enter a question to answer")

# who is or userinfo command


@client.command(aliases=["whois"])
async def userinfo(ctx, member: discord.Member = None):
    if not member:  # if member is no mentioned
        member = ctx.message.author  # set member as the author
    roles = [role for role in member.roles]

    embed = discord.Embed(colour=discord.Colour.dark_purple(), timestamp=ctx.message.created_at,
                          title=f"User Info - {member}", inline=False)
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_footer(text=f"Requested by {ctx.author}")

    embed.add_field(name="ID:", value=member.id)
    embed.add_field(name="Display Name:",
                    value=member.display_name, inline=False)

    embed.add_field(name="Created Account On:", value=member.created_at.strftime(
        "%a, %#d %B %Y, %I:%M %p UTC"), inline=False)
    embed.add_field(name="Joined Server On:", value=member.joined_at.strftime(
        "%a, %#d %B %Y, %I:%M %p UTC"), inline=False)

    embed.add_field(name="Roles:", value="  ".join(
        [role.mention for role in roles]), inline=False)
    embed.add_field(name="Highest Role:",
                    value=member.top_role.mention, inline=False)
    print(member.top_role.mention)
    await ctx.send(embed=embed)

# credits


@client.command()
async def credits(ctx):
    creditEmbed = discord.Embed(title="Credits of this project",
                                value="for these amazing guys this project is here", color=discord.Color.dark_purple())
    creditEmbed.add_field(
        name="Idea From", value="Professor.#2390, Tango#0001, ShxZa#6969")
    creditEmbed.add_field(name="Devs", value="Professor.#2390, ShxZa#6969")
    creditEmbed.add_field(name="Inspired By", value="Dank memer and MainBot")
    await ctx.send(embed=creditEmbed)


@client.command()
async def realcredits(ctx):
    realcreditEmbed = discord.Embed(
        title="Real Credits", color=discord.Color.dark_purple())
    realcreditEmbed.add_field(
        name="credit:", value="Sike every credit is my they stole it from me...")
    await ctx.send(embed=realcreditEmbed)

# loading cogs

for i in range(len(cogs)):
    cogs[i].setup(client)
    print("cog setup done")

# Running using the token
client.run(TOKEN)