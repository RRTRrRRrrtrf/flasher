import discord
from discord.ext import commands, tasks
import urllib.parse
import io
import time
from random import randint
from naomi_paginator import Paginator  # pylint: disable=import-error
from utils.errors import PrefixTooLong  # pylint: disable=import-error


class Other(commands.Cog):
    """Другие команды
    Комманды которым не нашлось другой категории."""

    def __init__(self, bot):
        self.bot = bot

    
    @commands.group(name="prefix", invoke_without_command=True)
    @commands.guild_only()
    async def prefix(self, ctx):
        """Просмотр префикса

        Для смены префикса используйте *`prefix set`*
        Пример: `prefix set F!`

        :warning: Бот чуствителен к регистру символов
        :memo: Исполнение комманды без указаного перефикса покажет вам какой у вас сейчас префикс"""

        server_data = await self.bot.sql(
            f"SELECT * FROM prefixes WHERE id={ctx.guild.id}"
        )
        user_data = await self.bot.sql(
            f"SELECT * FROM prefixes WHERE id={ctx.author.id}"
        )

        if not server_data:  # <Record > case
            server_prefix = self.bot.config["prefix"]
        else:
            server_prefix = server_data["value"]

        if not user_data:  # <Record > case
            user_prefix = self.bot.config["prefix"]
        else:
            user_prefix = user_data["value"]

        embed = discord.Embed(
            description="На сервере установлен префикс **`%s`**" % server_prefix,
            color=discord.Colour.gold(),
        )
        embed.add_field(
            name="Персональный префикс",
            value="У вас установлен префикс **`%s`**" % user_prefix,
        )
        embed.set_author(
            name=ctx.message.author.name, icon_url=str(ctx.author.avatar_url)
        )
        embed.set_footer(text=f"{ctx.prefix}{ctx.command}")
        await ctx.send(embed=embed)

    @prefix.command(name="guild", aliases=["server"])
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    @commands.cooldown(1, 15, commands.BucketType.guild)
    async def prefix_guild(self, ctx, prefix):
        """Смена префикса сервера

        Для смены префикса используйте *`prefix guild`*
        Пример: `prefix guild F!`

        :warning: Бот чуствителен к регистру символов
        :memo: Исполнение комманды без указаного перефикса покажет вам какой у вас сейчас префикс"""

        if len(prefix) > 7:
            raise PrefixTooLong()

        await self.bot.sql(
            f"INSERT INTO prefixes (id, value) VALUES ($1,$2)"
            "ON CONFLICT (id) DO UPDATE SET value = excluded.value;",
            ctx.guild.id,
            prefix,
        )

        embed = discord.Embed(
            description="На сервере успешно установлен префикс %s" % prefix,
            color=discord.Colour.green(),
        )
        embed.set_author(
            name=ctx.message.author.name, icon_url=str(ctx.author.avatar_url)
        )
        await ctx.send(embed=embed)

    @prefix.command(name="self", aliases=["user"])
    @commands.cooldown(1, 8, commands.BucketType.user)
    async def prefix_self(self, ctx, prefix):
        """Смена персонального префикса

        Для смены префикса используйте *`prefix self`*
        Пример: `prefix self F!`

        :warning: Бот чуствителен к регистру символов
        :memo: Исполнение комманды без указаного перефикса покажет вам какой у вас сейчас префикс"""

        if len(prefix) > 7:
            raise PrefixTooLong()

        await self.bot.sql(
            f"INSERT INTO prefixes VALUES ($1,$2) "
            "ON CONFLICT (id) DO UPDATE SET value = excluded.value;",
            ctx.author.id,
            prefix,
        )
        # except postgrelib_exceptions._base.InterfaceError: pass

        embed = discord.Embed(
            description="Персональный префикс %s успешно установлен" % prefix,
            color=discord.Colour.green(),
        )
        embed.set_author(
            name=ctx.message.author.name, icon_url=str(ctx.author.avatar_url)
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Other(bot))
