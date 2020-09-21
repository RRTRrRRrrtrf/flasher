import discord
from discord.ext import commands, tasks

import urllib.parse
import io
import time
from random import randint
from naomi_paginator import Paginator 

from utils.errors import PrefixTooLong  # pylint: disable=import-error
from utils.db import PrefixesSQL # pylint: disable=import-error

class Other(commands.Cog):
    """Другие команды
    Комманды которым не нашлось другой категории."""

    def __init__(self, bot):
        self.bot = bot
        self.db = PrefixesSQL(bot.db, bot.config)
    
    @commands.group(name="prefix", invoke_without_command=True)
    async def prefix(self, ctx):
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
        embed.set_footer(text=f"{ctx.prefix}{ctx.command} • Префикс не имеет приоритета если солпадает с стандратным")

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


def setup(bot):
    bot.add_cog(Other(bot))
