import discord
from discord.ext import commands, tasks
from time import time
from random import randint

class Economy(commands.Cog):
    """Команды экономики"""

    def __init__(self, bot):
        
        self.bot = bot
        self.commands_in_hour = 100
        self.Treasury_id = 10000000000000000 # If changed do INSERT INTO eco VALUES (new_id_here,0)



    @commands.Cog.listener()
    async def on_command_completion(self, ctx: commands.Context):
        self.commands_in_hour += 1



    @tasks.loop(hours=1)
    async def money_create(self):
        
        coins_to_add = round(self.commands_in_hour / 20)
        status_now = await self.bot.sql(
            "SELECT * FROM eco WHERE id=$1;", self.Treasury_id)
        
        coins_to_add += status_now[0]
        await self.bot.sql(
            "UPDATE eco SET coins=$2 WHERE id=$1;", self.Treasury_id, coins_to_add)
        
        self.commands_in_hour = 0



    @commands.command()
    @commands.cooldown(1,3600, commands.BucketType.user)
    async def work(self,ctx):
        """Заработайте Flasher Coins"""
        percentage = randint(1,8)/100 # 1-8% 
        tax_percentage = randint(10,45)/100 # 10-45% of 1-8% treasury 
        
        treasury_coins = (await self.bot.sql(
            "SELECT * FROM eco WHERE id=$1;", self.Treasury_id))['coins']
        has = (await self.bot.sql(
            "SELECT * FROM eco WHERE id=$1;", ctx.author.id))
        
        if not has: # [] case
            await self.bot.sql('INSERT INTO eco VALUES ($1, 0)', ctx.author.id)
            has = 0
        else:
            has = has['coins']
        
        full = treasury_coins * percentage
        deFacto = full - full*tax_percentage
        
        await self.bot.sql("UPDATE eco SET coins=$1 WHERE id=$2", 
                           treasury_coins - deFacto, self.Treasury_id)
        await self.bot.sql("UPDATE eco SET coins=$1 WHERE id=$2", 
                           has+deFacto, ctx.author.id)
        
        embed = discord.Embed(title='На баланс засчитано %s FlC' % deFacto,
                              description=f"""Заработок: {full},
                              Налоговый сбор {full-deFacto},
                              Состояние баланса {deFacto+has}.""",
                              color=discord.Colour.green())
        
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Economy(bot))
