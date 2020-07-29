import discord
from discord.ext import commands
import time
import random
from naomi_paginator import Paginator



class user_tools(commands.Cog):
    """Команды по работе с пользователями"""
    def __init__(self,bot):
        self.bot = bot



    @commands.command(aliases=['randM','randomNem','giveawayNow','randMember','rMember','rm'])
    async def randomMember(self,ctx,*,textArg):
        memberList = []
        for m in ctx.guild.members:
            if not m.bot:
                memberList.append(m.id)

        emb = discord.Embed(description=f'<@{random.choice(memberList)}> получает {textArg} от <@{ctx.author.id}>')
        emb.set_author(name=ctx.message.author.name, icon_url= str(ctx.author.avatar_url))
        emb.set_footer(text=f'{ctx.prefix}{ctx.command}' )
        await ctx.send(embed=emb)



    @commands.command(aliases=['myDiscriminator'])
    async def mytag(self,ctx):
        """Ники пользователей который имеют такой же дискриминатор как и у вас
        
        Сменив ваш ник на один из таких ваш дискриминатор сменится на случайный
        :warning: Discord устанавливает ограничения на смену ника и дискриминатора при нескольких использованиях"""
        
        names =[user.name
                for user in self.bot.users
                if user.name != ctx.author.name
                and ctx.author.discriminator == user.discriminator]
        random.shuffle(names)
        
        if len(names) > 100:
            names = names[:100]
        if len(names) == 0:
            return await ctx.send(':no_entry: Нам не удалось найти кого либо с таким же дискриминатором как у вас')
            
        p = Paginator(ctx)
        
        for name in names:
            p.add_page(
                discord.Embed(
                    title=name,
                    color = random.randint(0x000000, 0xFFFFFF)
                )
                .set_footer(text='Смена вашего ника на какой либо из представленных повлечёт смену '
                    f'вашего дискриминатора ({ctx.author.discriminator}) на случайный'))
                
        await p.call_controller()


def setup(bot):
    bot.add_cog(user_tools(bot))