import discord
from discord.ext import commands
import time


class Unknown(commands.Cog):

    def __init__(self,bot):
        self.bot = bot

    

    
    @commands.command(aliases = ["�🏓", 'pong', 'latency'])
    async def ping(self,ctx):
        await ctx.send(f':ping_pong: {round(self.bot.latency * 1000)}ms')

    @commands.command()
    @commands.is_owner()
    async def blacklistUser(self,ctx,id: str):
        bl = await self.bot.read_json('blacklist.json')
        bl["users"].append(id)
        await self.bot.write_json('blacklist.json', bl)
        await ctx.send('> OK')

    @commands.command()
    @commands.is_owner()
    async def blacklistServer(self,ctx,id: str):
        bl = await self.bot.read_json('blacklist.json')
        bl["servers"].append(id)
        await self.bot.write_json('blacklist.json', bl)
        await ctx.send('> OK')

    @commands.command()
    @commands.is_owner()
    async def pardonUser(self,ctx,id: str):
        bl = await self.bot.read_json('blacklist.json')
        bl["users"].remove(id)
        await self.bot.write_json('blacklist.json', bl)
        await ctx.send('> OK')

    @commands.command()
    @commands.is_owner()
    async def pardonServer(self,ctx,id: str):
        bl = await self.bot.read_json('blacklist.json')
        bl["servers"].remove(id)
        await self.bot.write_json('blacklist.json', bl)
        await ctx.send('> OK')







def setup(bot):
    bot.add_cog(Unknown(bot))