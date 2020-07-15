import discord
from discord.ext import commands, tasks
import urllib.parse
import io
import requests
import time
from random import randint
from naomi_paginator import Paginator
from utils.errors import PrefixTooLong # pylint: disable=import-error

class Other(commands.Cog):
    """Другие команды
    Комманды которым не нашлось другой категории."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 60)
    async def tts(self, ctx, *, text):
        """Озвучка введённого вами текста
        
        Пример: `f.tts Мой прекрасный текст`
        
        :warning: Комманда использует украинскоязычный TTS"""

        req = requests.get(
            f"http://78.47.9.109/tts/dospeech.php?apikey=freekey&deviceType=ogg&action=tts&text={urllib.parse.quote(text)}"
        )

        if req.status_code == 414:
            ctx.send("> Ошибка: слишком много символов")
            return

        byte = io.BytesIO(req.content)
        byte.seek(0)

        await ctx.send(
            "> Вы можете использовать + после гласной что бы изменить ударение. \n\n Результат:",
            file=discord.File(byte, filename="tts.ogg"),
        )

    @commands.command()
    async def invite(self, ctx):
        """ Пригласите бота на ваш сервер """

        emb = discord.Embed(
            title="Кастомизируйте права бота",
            description=f"[Приглашение со всеми правами](https://discordapp.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=-1&scope=bot)",
            color=discord.Colour.gold(),
        )
        emb.set_author(
            name=ctx.message.author.name, icon_url=str(ctx.author.avatar_url)
        )
        emb.set_footer(text=f"{ctx.prefix}{ctx.command}")
        emb.add_field(
            name="Пригласите бота без прав",
            value=f"[Бот не создаёт свою личную роль](https://discordapp.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=0&scope=bot)",
            inline=False,
        )
        emb.add_field(
            name="Пригласите бота с правом администратора",
            value=f"[Бот будет иметь права администратора](https://discordapp.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot)",
            inline=False,
        )
        invite = self.bot.config["supportServerInvite"]
        emb.add_field(
            name="Сервер поддержки",
            value=f"[Посетите сервер поддержки бота]({invite})",
            inline=False,
        )

        await ctx.send(embed=emb)

    @commands.group(name='prefix',invoke_without_command=True)
    @commands.guild_only()
    async def prefix(self, ctx):
        f"""Просмотр префикса
        
        Для смены префикса используйте *`prefix set`*
        Пример: `{ctx.prefix}prefix set F!`
        
        :warning: Бот чуствителен к регистру символов
        :memo: Исполнение комманды без указаного перефикса покажет вам какой у вас сейчас префикс """

        server_data = await self.bot.sql(f'SELECT * FROM prefixes WHERE id={ctx.guild.id}')
        user_data = await self.bot.sql(f'SELECT * FROM prefixes WHERE id={ctx.author.id}')
        
        if not server_data: # <Record > case
            server_prefix = self.bot.config["prefix"]
        else:
            server_prefix = server_data["value"]

        if not user_data: # <Record > case
            user_prefix = self.bot.config["prefix"]
        else:
            user_prefix = user_data["value"]

        embed = discord.Embed(description='На сервере установлен префикс **`%s`**' % server_prefix,color=discord.Colour.gold())
        embed.add_field(name='Персональный префикс', value='У вас установлен префикс **`%s`**' % user_prefix)
        embed.set_author(name=ctx.message.author.name, icon_url=str(ctx.author.avatar_url))
        embed.set_footer(text=f'{ctx.prefix}{ctx.command}')
        await ctx.send(embed=embed)
    

    @prefix.command(name='guild', aliases=['server'])
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    @commands.cooldown(1,15,commands.BucketType.guild)
    async def prefix_guild(self,ctx,prefix):
        f"""Смена префикса сервера
        
        Для смены префикса используйте *`prefix guild`*
        Пример: `{ctx.prefix}prefix guild F!`
        
        :warning: Бот чуствителен к регистру символов
        :memo: Исполнение комманды без указаного перефикса покажет вам какой у вас сейчас префикс """
        
        if len(prefix) > 7: raise PrefixTooLong()
        
        await self.bot.sql(f'INSERT INTO prefixes (id, value) VALUES ($1,$2)'
                            'ON CONFLICT (id) DO UPDATE SET value = excluded.value;', ctx.guild.id, prefix)
                            
        embed = discord.Embed(description='На сервере успешно установлен префикс %s' % prefix,color=discord.Colour.green())
        embed.set_author(name=ctx.message.author.name, icon_url=str(ctx.author.avatar_url))
        await ctx.send(embed=embed)



    @prefix.command(name='self', aliases=['user'])
    @commands.cooldown(1,8,commands.BucketType.user)
    async def prefix_self(self,ctx,prefix):
        f"""Смена персонального префикса
        
        Для смены префикса используйте *`prefix self`*
        Пример: `{ctx.prefix}prefix self F!`
        
        :warning: Бот чуствителен к регистру символов
        :memo: Исполнение комманды без указаного перефикса покажет вам какой у вас сейчас префикс """
        
        if len(prefix) > 7: raise PrefixTooLong()

        await self.bot.sql(f'INSERT INTO prefixes VALUES ($1,$2) '
                            'ON CONFLICT (id) DO UPDATE SET value = excluded.value;', ctx.author.id, prefix)
        #except postgrelib_exceptions._base.InterfaceError: pass
        
        embed = discord.Embed(description='Персональный префикс %s успешно установлен' % prefix,color=discord.Colour.green())
        embed.set_author(name=ctx.message.author.name, icon_url=str(ctx.author.avatar_url))
        await ctx.send(embed=embed)



    @commands.command(name="help", aliases=["commands", "cmds"])
    async def thelp(self, ctx, *, command: str = None):
        """Справочник по командам.
        """

        if command is None:

            p = Paginator(ctx)
            embed = discord.Embed(
                timestamp=ctx.message.created_at,
                color=randint(0x000000, 0xFFFFFF),
                title="Справочник по командам",
            )
            __slots__ = []

            for cog in self.bot.cogs:
                __slots__.append(self.bot.get_cog(cog))

            emb = discord.Embed(
                title="Обратите внимание",
                description="Если по какой то из причин стрелки для переключения страниц помощи по коммандах не работают вы можете использовать комманду `simplehelp`",
                color=discord.Colour.light_grey(),
            )
            emb.set_thumbnail(url=self.bot.user.avatar_url)
            emb.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            emb.set_footer(
                text=f"{ctx.prefix}help [команда/категория] для получения доп.информации."
            )
            #p.add_page(emb)
            del emb

            for cog in __slots__:
                cog_info = cog.__class__.__doc__.partition('\n')  # (name, partitionSymboll, description)
                cog_commands = len(
                    [
                        x
                        for x in self.bot.commands
                        if x.cog_name == cog.__class__.__name__ and not x.hidden
                    ]
                )
                if cog_commands == 0:
                    pass
                else:
                    embed.add_field(
                        name=cog_info[0],
                        value=", ".join(
                            [
                                f"`{x}`"
                                for x in self.bot.commands
                                if x.cog_name == cog.__class__.__name__ and not x.hidden
                            ]
                        ),
                        inline=False,
                    )
                    embed.set_thumbnail(url=self.bot.user.avatar_url)
                    embed.set_author(
                        name=ctx.author.name, icon_url=ctx.author.avatar_url
                    )
                    embed.set_footer(
                        text=f"{ctx.prefix}help [команда/категория] для получения доп.информации."
                    )
                    p.add_page(embed)

                    embed = discord.Embed(
                        timestamp=ctx.message.created_at,
                        color=randint(0x000000, 0xFFFFFF),
                        title="Справочник по командам",
                    )

            await p.call_controller()

        else:
            entity = self.bot.get_cog(command) or self.bot.get_command(command)

            if entity is None:
                clean = command.replace("@", "@\u200b")
                embed = discord.Embed(
                    timestamp=ctx.message.created_at,
                    color=randint(0x000000, 0xFFFFFF),
                    title="Справочник по командам",
                    description=f'Команда или категория "{clean}" не найдена.',
                )

            elif isinstance(entity, commands.Command):
                embed = discord.Embed(
                    timestamp=ctx.message.created_at,
                    color=randint(0x000000, 0xFFFFFF),
                    title="Справочник по командам",
                )
                embed.add_field(
                    name=f"{ctx.prefix}{entity.name} {entity.signature}",
                    value=entity.help,
                    inline=False,
                )

                if entity.aliases:
                    embed.add_field(
                        name="Варианты использования",
                        value=",".join([f"`{x}`" for x in entity.aliases]),
                        inline=False,
                    )

            else:
                embed = discord.Embed(
                    timestamp=ctx.message.created_at,
                    color=randint(0x000000, 0xFFFFFF),
                    title="Справочник по командам",
                )
                cog_info = entity.__class__.__doc__.partition('\n') # (name, partitionSymboll, description)
                embed.add_field(
                    name=cog_info[0],
                    value=", ".join(
                        [
                            f"`{x}`"
                            for x in self.bot.commands
                            if x.cog_name == entity.__class__.__name__ and not x.hidden
                        ]
                    ),
                    inline=False,
                )

            embed.set_thumbnail(url=self.bot.user.avatar_url)
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            embed.set_footer(
                text=f"{ctx.prefix}help [команда/категория] для получения доп.информации."
            )

            await ctx.send(embed=embed)

    @commands.command(aliases=["simplecommands", "simplecmds"])
    async def simplehelp(self, ctx):
        """Справочник по командам.
        Для того что бы уточнить предназначение комманды используйте `help`!
        """
        embed = discord.Embed(
            timestamp=ctx.message.created_at,
            color=randint(0x000000, 0xFFFFFF),
            title="Справочник по командам",
        )
        __slots__ = []

        for cog in self.bot.cogs:
            __slots__.append(self.bot.get_cog(cog))

        for cog in __slots__:
            cog_commands = len(
                [
                    x
                    for x in self.bot.commands
                    if x.cog_name == cog.__class__.__name__ and not x.hidden
                ]
            )
            if cog_commands == 0:
                pass
            else:
                embed.add_field(
                    name=cog.__class__.__doc__.partition('\n')[0],
                    value=", ".join(
                        [
                            f"`{x}`"
                            for x in self.bot.commands
                            if x.cog_name == cog.__class__.__name__ and not x.hidden
                        ]
                    ),
                    inline=False,
                )

        await ctx.send(embed=embed)

    @commands.command(aliases=["�🏓", "pong", "latency"])
    async def ping(self, ctx):
        await ctx.send(f":ping_pong: {round(self.bot.latency * 1000)}ms")



def setup(bot):
    bot.add_cog(Other(bot))



