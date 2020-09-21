import discord
from discord.ext import commands, tasks

from naomi_paginator import Paginator 
from random import choice

from utils.errors import PrefixTooLong  # pylint: disable=import-error
from utils.db import PrefixesSQL # pylint: disable=import-error

class Other(commands.Cog):
    """Другие команды
    Комманды которым не нашлось другой категории."""

    def __init__(self, bot):
        self.bot = bot
        self.db = PrefixesSQL(bot.db, bot.config)
        self.status_loop.start() # pylint: disable=no-member
    
    @commands.group(name="prefix", invoke_without_command=True)
    async def prefix(self, ctx, disable_footer=False): # disable_footer unrecheable from message
        """Просмотр префикса
        Для смены префикса используйте *`prefix guild/user`*
        
        :memo: Самый большой приоритет имеет персональный префикс, но приоритет исчезает если префикс солпадает с стандартным префиксом бота"""
        
        user_prefix = await self.db.get(ctx.author)

        embed = discord.Embed(description="Ваш персональный префикс **`%s`**" % user_prefix,
            color=discord.Colour.gold())

        embed.add_field(name="Префикс сервера",
            value="На этом сервере установлен префикс **`%s`**" % await self.db.get(ctx.guild)
        ) if ctx.guild else None

        embed.set_author(name=ctx.message.author.name, icon_url=str(ctx.author.avatar_url))
        embed.set_footer(text=f" {ctx.prefix + ctx.command.name + ' • ' if not disable_footer else ''}Префикс не имеет приоритета если солпадает с стандратным") 

        await ctx.send(embed=embed)

    @prefix.command(name="guild", aliases=["server"])
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    @commands.cooldown(1, 15, commands.BucketType.guild)
    async def prefix_guild(self, ctx, prefix=None):
        """Смена префикса сервера

        Для смены префикса используйте *`prefix guild`*
        Пример: `prefix guild F!`

        :warning: Бот чуствителен к регистру символов
        :memo: Исполнение комманды без указаного перефикса покажет вам какой у вас сейчас префикс"""
        if not prefix:
            prefix = self.bot.config.get('prefix')

        if len(prefix) > 7:
            raise PrefixTooLong()

        is_reseted = await self.db.set(ctx.guild, prefix) # Returns 'Prefix reseted' if prefix reseted

        embed = discord.Embed(
            description="На сервере успешно установлен префикс %s" % prefix,
            color=discord.Colour.green(),
        ) if not is_reseted else discord.Embed(description='Префикс сервера сброшен')
        
        embed.set_author(name=ctx.message.author.name, icon_url=str(ctx.author.avatar_url))
        
        await ctx.send(embed=embed)

    @prefix.command(name="self", aliases=["user"])
    @commands.cooldown(1, 8, commands.BucketType.user)
    async def prefix_self(self, ctx, prefix=None):
        """Смена персонального префикса

        Для смены префикса используйте *`prefix self`*
        Пример: `prefix self F!`        Для смены префикса используйте *`prefix self`*
        Пример: `prefix self F!`

        :warning: Бот чуствителен к регистру символов
        :memo: Исполнение комманды без указаного перефикса покажет вам какой у вас сейчас префикс"""

        if not prefix:
            prefix = self.bot.config.get('prefix')

        if len(prefix) > 7:
            raise PrefixTooLong()

        is_reseted = await self.db.set(ctx.author, prefix) # Returns 'Prefix reseted' if prefix reseted

        embed = discord.Embed(
            description="Ваш новый персональный префикс - `%s`" % prefix,
            color=discord.Colour.green(),
        ) if not is_reseted else discord.Embed(description='Персональный префикс сброшен')
        
        embed.set_author(name=ctx.message.author.name, icon_url=str(ctx.author.avatar_url))
        
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.content != f"<@!{self.bot.user.id}>" or msg.author.bot:
            return
        ctx = await self.bot.get_context(msg)
        await self.prefix(ctx, disable_footer=True)

    @tasks.loop(seconds=45.0)
    async def status_loop(self):
        status = (
            f'{self.bot.config.get("prefix")}help | {len(self.bot.users)} пользователь(ей)',
            f'{self.bot.config.get("prefix")}help | {len(self.bot.guilds)} сервер(ов)',
            f'{self.bot.config.get("prefix")}help для просмотра списка команд')
        s = choice(status)
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(s))

def setup(bot):
    bot.add_cog(Other(bot))
