import discord
from discord.ext import commands
import time
import requests
import humanize
import urllib.parse
import random
import datetime

bot = commands.Bot(command_prefix='/')
rID = 0

class Number_tools(commands.Cog):

    def __init__(self,bot):
        self.bot = bot

    

    @commands.command(aliases=['calc','expr','expresion'])
    async def calculate(self,ctx,*,toCalc):
        '''Математические обчисления с помощью API https://api.mathjs.org
        
        Пример: `/calc sqrt(7)*4+2` -> `((7^2) * 4) +2` -> Результат: `198`
        
        '''
        response = requests.get(f"http://api.mathjs.org/v4/?expr={urllib.parse.quote(toCalc.replace('**','^'))}")
        emb = discord.Embed(title='Обчислить значение',description=f'Результат обчисления ```{response.text}```',color=discord.Colour.gold())
        emb.set_author(name=ctx.message.author.name, icon_url= str(ctx.author.avatar_url))
        emb.set_footer(text='/calc | https://api.mathjs.org')
        await ctx.send(embed=emb)



    @commands.command(aliases=['advancedFloat','convertFloat','cf','convert_float','deciminalToFloat'])
    async def advFloat(self,ctx,toNat: float):
        '''Превращение десятичных дробей в обычные дроби

        Пример: `/convertFloat 1.3939393939393939` (1.(39)) -> `1 13/33` 
        '''
        toNat = humanize.fractional(toNat)
        emb = discord.Embed(title='Превратить десятичное число в обычную дробь',description=f'Превращённое число ```{toNat}```',color=discord.Colour.gold())
        emb.set_author(name=ctx.message.author.name, icon_url= str(ctx.author.avatar_url))
        emb.set_footer(text='/advancedFloat')
        await ctx.send(embed=emb)    






def setup(bot):
    bot.add_cog(Number_tools(bot))