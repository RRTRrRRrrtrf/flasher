import discord
from discord.ext import commands
import time
import random



#from mojang_api import Player
#from currency_converter import CurrencyConverter
class other(commands.Cog):

    def __init__(self,bot):
        self.bot = bot
        self.deleted = ''








    @commands.command()
    async def invite(self,ctx):
        ''' Пригласите бота на ваш сервер '''
        emb = discord.Embed(title='Кастомизируйте права бота',description='[Приглашение со всеми правами](https://discordapp.com/api/oauth2/authorize?client_id=677176212518600714&permissions=-1&scope=bot)',color=discord.Colour.gold())
        emb.set_author(name=ctx.message.author.name, icon_url= str(ctx.author.avatar_url))
        emb.set_footer(text='/invite')
        emb.add_field(name='Пригласите бота без прав',value='[Бот не создаёт свою личную роль](https://discordapp.com/api/oauth2/authorize?client_id=677176212518600714&permissions=0&scope=bot)',inline=False)
        emb.add_field(name='Пригласите бота с правом администратора',value='[Бот будет иметь права администратора](https://discordapp.com/api/oauth2/authorize?client_id=677176212518600714&permissions=8&scope=bot)',inline=False)
        emb.add_field(name='Саппорт сервер',value='[URAN](https://discord.gg/KeQ2eEM)',inline=False)
        await ctx.send(embed=emb)

    @commands.command()
    async def prefix(self,ctx,pref = None):
        if not pref:
            try: prefNow = await self.bot.read_json('data.json'); prefNow = prefNow['prefixes'][str(ctx.author.id)]
            except: prefNow = '/'
            emb = discord.Embed(title='Используйте /prefix {ваш префикс}',description=f'У вас установлен префикс ``{prefNow}``',color=discord.Colour.gold())
            emb.set_author(name=ctx.message.author.name, icon_url= str(ctx.author.avatar_url))
            emb.set_footer(text='/invite')    
            await ctx.send(embed=emb)        
        else:
            data = await self.bot.read_json('data.json')
            data["prefixes"][str(ctx.author.id)] = pref
            await self.bot.write_json('data.json',data)
            emb = discord.Embed(title='Префикс успешно изменён',description='Ваш префикс бота изменён',color=discord.Colour.green())
            emb.set_author(name=ctx.message.author.name, icon_url= str(ctx.author.avatar_url))
            emb.set_footer(text='/invite')    
            await ctx.send(embed=emb)                    


"""    @commands.Cog.listener()
    async def on_message_delete(self,ctx):
        self.deleted= f'Последнее удалённое сообщение ``{ctx.message.content}`` от {ctx.author.mention}'

    @commands.command()
    @commands.guild_only()
    async def lastDel(self,ctx): 
        ''' Последнее удалённое сообщение '''
        try:
            emb = discord.Embed(description=self.deleted, color = discord.Colour.darker_grey())
            emb.set_author(name=ctx.author.name, icon_url= str(ctx.author.avatar_url))
            emb.set_footer(text='/lastDel')
            await ctx.send(embed=emb)
        except:
            emb = discord.Embed(description='Удалённое сообщение не зафиксировано',color=discord.Colour.red())
            emb.set_author(name=ctx.message.author.name, icon_url= str(ctx.author.avatar_url))
            emb.set_footer(text='/lastDel')
            await ctx.send(embed=emb)            

"""



 









def setup(bot):
    bot.add_cog(other(bot))