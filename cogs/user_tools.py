import discord
from discord.ext import commands
import time
import random



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





def setup(bot):
    bot.add_cog(user_tools(bot))