import discord
from discord.ext import commands, tasks
from pymongo import MongoClient

bot_channel = 877454309560815636
talk_channels = [860725489526112256, 860749614268809227, 869090593748430908]
level = ["Beginner (LVL.5)", "Active (LVL.15)",
         "Advance (LVL.25)", "God Like (lvl.50)"]
levelnum = [5, 15, 25, 50]

cluster = MongoClient(
    "mongodb+srv://void:voidbot@cluster0.gxld3.mongodb.net/discord?retryWrites=true&w=majority")

leveling = cluster["discord"]["leveling"]


class levelsys(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("ready")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id in talk_channels:
            stats = leveling.find_one({"id": message.author.id})
            if not message.author.bot:
                if stats is None:
                    newuser = {"id": message.author.id, "xp": 100}
                    leveling.insert_one(newuser)
                else:
                    xp = stats["xp"] + 5
                    leveling.update_one({"id": message.author.id}, {
                                        "$set": {"xp": xp}})
                    lvl = 0
                    while True:
                        if xp < ((50*(lvl**2))+(50*lvl)):
                            break
                        lvl += 1
                    xp -= ((50*((lvl-1)**2))+(50*(lvl-1)))
                    if xp == 0:
                        await message.channel.send(f"well done {message.author.mention}! you leveled up to **lvl: {lvl}**!")
                        for i in range(len(level)):
                            if lvl == levelnum[i]:
                                await message.author.add_roles(discord.utils.get(message.author.guild.roles, name=level[i]))
                                embed = discord.Embed(
                                    description=f'{message.author.mention} you have gotten role **{level[i]}**!')
                                embed.set_thumbnail(
                                    url=message.author.avatar_url)
                                await channel.send(embed=embed)

    @commands.command()
    async def rank(self, ctx):
        if ctx.channel.id == bot_channel:
            stats = leveling.find_one({"id": ctx.author.id})
            if stats is None:
                embed = discord.Embed(
                    description="You haven't sent any messages, no rank!!!")
                await ctx.channel.send(embed=embed)
            else:
                xp = stats["xp"]
                lvl = 0
                rank = 0
                while True:
                    if xp < ((50*(lvl**2))+(50*lvl)):
                        break
                    lvl += 1
                xp -= ((50*((lvl-1)**2))+(50*(lvl-1)))
                boxes = int((xp/(200*((1/2) * lvl)))*20)
                rankings = leveling.find().sort("xp", -1)
                for x in rankings:
                    rank += 1
                    if stats["id"] == x["id"]:
                        break
                embed = discord.Embed(
                    title="{}'s level stats".format(ctx.author.name))
                embed.add_field(
                    name="Name", value=ctx.author.mention, inline=True)
                embed.add_field(
                    name="XP", value=f"{xp}/{int(200*((1/2)*lvl))}", inline=True)
                embed.add_field(
                    name="Rank", value=f"{rank}/{ctx.guild.member_count}", inline=True)
                embed.add_field(name="Progress Bar [lvl]", value=boxes * ":blue_square:" + (
                    20-boxes) * ":white_large_square:", inline=False)
                embed.set_thumbnail(url=ctx.author.avatar_url)
                await ctx.channel.send(embed=embed)

    @commands.command()
    async def leader_board(self, ctx):
        if(ctx.channel.id == bot_channel):
            rankings = leveling.find().sort("xp", -1)
            i = 1

            embed = discord.Embed(title="Rankings:")
            for x in rankings:
                try:
                    temp = ctx.guild.get_member(x["id"])
                    tempxp = x["xp"]
                    embed.add_field(
                        name=f"{i}: {temp.name}", value=f"Total XP: {tempxp}", inline=False)
                    i += 1
                except:
                    pass

                if i == 11:
                    break

            await ctx.channel.send(embed=embed)

def setup(client):
    client.add_cog(levelsys(client))