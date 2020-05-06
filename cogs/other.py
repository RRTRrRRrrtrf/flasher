import discord
from discord.ext import commands
import time
import random
import urllib.parse
import io
import requests
from random import randint
from paginator import Paginator



#from mojang_api import Player
#from currency_converter import CurrencyConverter
class Other(commands.Cog):

    def __init__(self,bot):
        self.bot = bot
        self.deleted = ''



    @commands.command()
    @commands.cooldown(1,60)
    async def tts(self,ctx,*,text):
        """Озвучка введённого вами текста
        
        Пример: `f.tts Мой прекрасный текст`
        
        :warning: Комманда использует украинскоязычный TTS"""
        
        req = requests.get(
            f'http://78.47.9.109/tts/dospeech.php?apikey=freekey&deviceType=ogg&action=tts&text={urllib.parse.quote(text)}')

        if req.status_code == 414: 
            ctx.send('> Ошибка: слишком много символов')
            return
        
        byte = io.BytesIO(req.content)
        byte.seek(0)

        await ctx.send('> Вы можете использовать + после гласной что бы изменить ударение. \n\n Результат:',
            file=discord.File(byte, filename='tts.ogg'))



    @commands.command()
    async def invite(self,ctx):
        ''' Пригласите бота на ваш сервер '''

        emb = discord.Embed(title='Кастомизируйте права бота',description='[Приглашение со всеми правами](https://discordapp.com/api/oauth2/authorize?client_id=677176212518600714&permissions=-1&scope=bot)',color=discord.Colour.gold())
        emb.set_author(name=ctx.message.author.name, icon_url= str(ctx.author.avatar_url))
        emb.set_footer(text=f'{ctx.prefix}{ctx.command}')
        emb.add_field(name='Пригласите бота без прав',value='[Бот не создаёт свою личную роль](https://discordapp.com/api/oauth2/authorize?client_id=677176212518600714&permissions=0&scope=bot)',inline=False)
        emb.add_field(name='Пригласите бота с правом администратора',value='[Бот будет иметь права администратора](https://discordapp.com/api/oauth2/authorize?client_id=677176212518600714&permissions=8&scope=bot)',inline=False)
        emb.add_field(name='Саппорт сервер',value='[URAN](https://discord.gg/KeQ2eEM)',inline=False)

        await ctx.send(embed=emb)



    @commands.command()
    async def prefix(self,ctx,pref = None):
        """ Измените свой префикс на такой что вам по душе.

        Пример: `f.prefix F!`
        
        :warning: Бот чуствителен к регистру символов
        :memo: Исполнение комманды без указаного перефикса покажет вам какой у вас сейчас префикс """

        if not pref:

            try: prefNow = await self.bot.read_json('data.json'); prefNow = prefNow['prefixes'][str(ctx.author.id)]
            except: prefNow = '/'

            emb = discord.Embed(title='Используйте /prefix {ваш префикс}',description=f'У вас установлен префикс ``{prefNow}``',color=discord.Colour.gold())
            emb.set_author(name=ctx.message.author.name, icon_url= str(ctx.author.avatar_url))
            emb.set_footer(text=f'{ctx.prefix}{ctx.command}') 

            await ctx.send(embed=emb)        
        else:

            data = await self.bot.read_json('data.json')
            data["prefixes"][str(ctx.author.id)] = pref

            await self.bot.write_json('data.json',data)

            emb = discord.Embed(title='Префикс успешно изменён',description='Ваш префикс бота изменён',color=discord.Colour.green())
            emb.set_author(name=ctx.message.author.name, icon_url= str(ctx.author.avatar_url))
            emb.set_footer(text=f'{ctx.prefix}{ctx.command}')  

            await ctx.send(embed=emb)                    



    @commands.command(name='help', aliases=['commands', 'cmds'])
    async def thelp(self, ctx, *, command: str = None):
        """Справочник по командам.
        """

        if command is None:
            
            p = Paginator(ctx)
            embed = discord.Embed(timestamp=ctx.message.created_at,
                            color=randint(0x000000, 0xFFFFFF),
                            title='Справочник по командам')
            __slots__ = []

            for cog in self.bot.cogs:
                __slots__.append(self.bot.get_cog(cog))

            emb = discord.Embed(title='Обратите внимание',
                description='Если по какой то из причин стрелки для переключения страниц помощи по коммандах не работают вы можете использовать комманду `simplehelp`',
                color=discord.Colour.light_grey())
            emb.set_thumbnail(url=self.bot.user.avatar_url)
            emb.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            emb.set_footer(text=f'{ctx.prefix}help [команда/категория] для получения доп.информации.')            
            p.add_page(emb)
            del emb

            for cog in __slots__:
                cog_commands = len([x for x in self.bot.commands if x.cog_name == cog.__class__.__name__ and not x.hidden])
                if cog_commands == 0:
                    pass
                else:
                    embed.add_field(name=cog.__class__.__name__,
                                    value=', '.join([f'`{x}`' for x in self.bot.commands if x.cog_name == cog.__class__.__name__ and not x.hidden]),
                                    inline=False)
                    embed.set_thumbnail(url=self.bot.user.avatar_url)
                    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                    embed.set_footer(text=f'{ctx.prefix}help [команда/категория] для получения доп.информации.')
                    p.add_page(embed)

                    embed = discord.Embed(timestamp=ctx.message.created_at,
                        color=randint(0x000000, 0xFFFFFF),
                        title='Справочник по командам')

            await p.call_controller()




        else:
            entity = self.bot.get_cog(command) or self.bot.get_command(command)

            if entity is None:
                clean = command.replace('@', '@\u200b')
                embed = discord.Embed(timestamp=ctx.message.created_at,
                                color=randint(0x000000, 0xFFFFFF),
                                title='Справочник по командам',
                                description=f'Команда или категория "{clean}" не найдена.')

            elif isinstance(entity, commands.Command):
                embed = discord.Embed(timestamp=ctx.message.created_at,
                                color=randint(0x000000, 0xFFFFFF),
                                title='Справочник по командам')
                embed.add_field(name=f'{ctx.prefix}{entity.name} {entity.signature}',
                                value=entity.help,
                                inline=False)

                if entity.aliases:
                    embed.add_field(name='Варианты использования',
                        value=",".join([f'`{x}`' for x in entity.aliases]),
                        inline=False) 

            else:
                embed = discord.Embed(timestamp=ctx.message.created_at,
                                color=randint(0x000000, 0xFFFFFF),
                                title='Справочник по командам')
                embed.add_field(name=entity.__class__.__name__ + ': ' + entity.__class__.__doc__,
                                value=', '.join([f'`{x}`' for x in self.bot.commands if x.cog_name == entity.__class__.__name__ and not x.hidden]),
                                inline=False)

            embed.set_thumbnail(url=self.bot.user.avatar_url)
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            embed.set_footer(text=f'{ctx.prefix}help [команда/категория] для получения доп.информации.')

            await ctx.send(embed=embed)



    @commands.command(aliases=['simplecommands', 'simplecmds'])
    async def simplehelp(self, ctx):
        """Справочник по командам.
        Для того что бы уточнить предназначение комманды используйте `help`!
        """
        embed = discord.Embed(timestamp=ctx.message.created_at,
                        color=randint(0x000000, 0xFFFFFF),
                        title='Справочник по командам')
        __slots__ = []

        for cog in self.bot.cogs:
            __slots__.append(self.bot.get_cog(cog))

        for cog in __slots__:
            cog_commands = len([x for x in self.bot.commands if x.cog_name == cog.__class__.__name__ and not x.hidden])
            if cog_commands == 0:
                pass
            else:
                embed.add_field(name=cog.__class__.__name__,
                                value=', '.join([f'`{x}`' for x in self.bot.commands if x.cog_name == cog.__class__.__name__ and not x.hidden]),
                                inline=False)
        
        await ctx.send(embed=embed)







def setup(bot):
    bot.add_cog(Other(bot))