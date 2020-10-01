import discord
from discord.ext import commands, tasks

import datetime
from naomi_paginator import Paginator 
from random import randint
from itertools import cycle

from utils.errors import PrefixTooLong, TooManyTries, CanceledByUser # pylint: disable=import-error
from utils.db import PrefixesSQL, IdeasSQL, DashboardSQL # pylint: disable=import-error

class DB:
    """Empty class for self.db.prefixes/ideas"""
    pass

class Other(commands.Cog):
    """Другие команды
    Комманды которым не нашлось другой категории."""

    def __init__(self, bot):
        self.bot = bot
        self.db = DB
        self.db.prefixes = PrefixesSQL(bot.db, bot.config)
        self.db.ideas = IdeasSQL(bot.db)
        self.db.dashboard = DashboardSQL(bot.db)
        self.status = None # Changes on_ready

    @commands.group(name="prefix", invoke_without_command=True)
    async def prefix(self, ctx, disable_footer=False): # disable_footer unrecheable from message
        """Просмотр префикса
        Для смены префикса используйте *`prefix guild/user`*
        
        :memo: Самый большой приоритет имеет персональный префикс, но приоритет исчезает если префикс солпадает с стандартным префиксом бота"""
        
        user_prefix = await self.db.prefixes.get(ctx.author)

        embed = discord.Embed(description="Ваш персональный префикс **`%s`**" % user_prefix,
            color=discord.Colour.gold())

        embed.add_field(name="Префикс сервера",
            value="На этом сервере установлен префикс **`%s`**" % await self.db.prefixes.get(ctx.guild)
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

        is_reseted = await self.db.prefixes.set(ctx.guild, prefix) # Returns 'Prefix reseted' if prefix reseted

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

        is_reseted = await self.db.prefixes.set(ctx.author, prefix) # Returns 'Prefix reseted' if prefix reseted

        embed = discord.Embed(
            description="Ваш новый персональный префикс - `%s`" % prefix,
            color=discord.Colour.green(),
        ) if not is_reseted else discord.Embed(description='Персональный префикс сброшен')
        
        embed.set_author(name=ctx.message.author.name, icon_url=str(ctx.author.avatar_url))
        
        await ctx.send(embed=embed)

    @commands.command(aliases=["suggestIdea", "bug", "idea"])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def suggest(self, ctx):
        """Подайте идею для бота"""

        def check(msg: discord.Message):
            return msg.author.id == ctx.author.id

        for i in range(5):
            await ctx.send(
                "Введите тему идеи (не больше 60 символов).\n"
                'Отправьте "Отмена" что бы отменить подачу идеи\n'
                'или "Пропустить" что бы не подавать тему для идеи\n', delete_after=60)

            msg = await self.bot.wait_for("message", check=check, timeout=60)
            topic = msg.content
            
            try:
                await msg.delete()
            except:
                pass

            if topic.lower() in ("skip", "пропустить", "пропуск", "скип"):
                topic = None
                break
            elif topic.lower() in ("отмена", "отменить", "cancel"):
                raise CanceledByUser()

            if len(topic) < 61:
                break
            else:
                await ctx.send('Слишком большая длина!', delete_after=5)
            if i == 4:
                raise TooManyTries()

        for i in range(5):
            await ctx.send(
                "Введите описание идеи (не больше 512 символов).\n"
                'Отправьте "Отмена" что бы отменить подачу идеи\n', delete_after=120)
            msg = await self.bot.wait_for("message", check=check, timeout=120)
            description = msg.content

            try:
                await msg.delete()
            except:
                pass

            if description.lower() in ("отмена", "отменить", "cancel"):
                raise CanceledByUser()
            if len(description) < 513:
                break
            else:
                await ctx.send('Слишком большая длина!', delete_after=5)
            if i == 4:
                raise TooManyTries()

        idea_number = await self.db.ideas.add(ctx.author, topic, description)

        if not topic:
            topic = "Тема не была установлена"

        channel = await self.bot.fetch_channel(self.bot.config["ideaChannel"])

        embed = discord.Embed(
            title=f"Идея #{idea_number} от {ctx.author.name} • {topic}",
            description=description,
            timestamp=datetime.datetime.now(),
        )
        embed.set_author(
            name=ctx.message.author.name, icon_url=str(ctx.author.avatar_url)
        )
        embed.set_footer(text="Идея была подана")

        await channel.send(embed=embed)

        embed = discord.Embed(
            title=f"Ваша идея #{idea_number} отправлена успешно",
            color=discord.Colour.green(),
            url=self.bot.config["supportServerInvite"],
        )
        embed.add_field(name=topic, value=description)

        await ctx.send(embed=embed)

    @commands.command(aliases=["db"])
    async def dashboard(self, ctx):
        """Последние 15 записей с сервера поддержки."""
        p = Paginator(ctx)
        data = await self.db.dashboard.get()

        for page in data:
            embed = discord.Embed(
                title=page["topic"],
                description=page["content"],
                timestamp=datetime.datetime.fromtimestamp(page["time"]),
                color=randint(0x000000, 0xFFFFFF))
            p.add_page(embed)

        embed = discord.Embed(
            title="Вы просмотрели последние записи",
            description="Последние 15 записей просмотрены",
            color=randint(0x000000, 0xFFFFFF))
        p.add_page(embed)

        await p.call_controller()

####### Events and tasks
    
    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.content != f"<@!{self.bot.user.id}>" or msg.author.bot:
            return
        ctx = await self.bot.get_context(msg)
        await self.prefix(ctx, disable_footer=True)

    @tasks.loop(seconds=45.0)
    async def status_loop(self):
        activity = discord.Game(next(self.status))
        await self.bot.change_presence(status=discord.Status.online, activity=activity)

    @commands.Cog.listener()
    async def on_ready(self):
        """Starts status loop on bot ready"""
        self.status = cycle((
            f'{self.bot.config.get("prefix")}help | {len(self.bot.users)} пользователь(ей)',
            f'{self.bot.config.get("prefix")}help | {len(self.bot.guilds)} сервер(ов)',
            f'{self.bot.config.get("prefix")}help для просмотра списка команд'))
        try:
            self.status_loop.start() # pylint: disable=no-member
        except RuntimeError: # Raises if loop already started (because on reconnect event invokes)
            pass

def setup(bot):
    bot.add_cog(Other(bot))
