import discord
from discord.ext import commands
import time




class Unknown(commands.Cog):

    def __init__(self,bot):
        self.bot = bot

    

    
    @commands.command(aliases = ["�🏓", 'pong', 'latency'])
    async def ping(self,ctx):
        await ctx.send(f':ping_pong: {round(self.bot.latency * 1000)}ms')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def blacklistUser(self,ctx,id:discord.Member):
        bl = await self.bot.read_json('blacklist.json')
        bl['users'].append(id.id)
        await self.bot.write_json('blacklist.json', bl)
        await ctx.send('> OK')


    @commands.command(hidden=True)
    @commands.is_owner()
    async def pardonUser(self,ctx,id: discord.Member):
        bl = await self.bot.read_json('blacklist.json')
        bl['users'].remove(id.id)
        await self.bot.write_json('blacklist.json', bl)
        await ctx.send('> OK')



    @commands.command(hidden=True)
    @commands.is_owner()
    async def migrate(self,ctx):
        t = await self.bot.read_json('config.json')
        if self.bot.http.token == t["token"]: 
            self.bot.http.token = t["token canary"]; await ctx.send('> OK')
        elif self.bot.http.token == t["token canary"]: 
            self.bot.http.token = t["token"]; await ctx.send('> OK')
        else: ctx.send('Invalid token provided')
        

    @commands.command(hidden=True)
    @commands.is_owner()
    async def shutdown(self,ctx,t: int):
        to = self.bot.http.token
        del self.bot.http.token
        time.sleep(t)
        self.bot.http.token = to
        await ctx.send('> Online')



def setup(bot):
    bot.add_cog(Unknown(bot))