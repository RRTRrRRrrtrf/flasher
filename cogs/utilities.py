import discord
from discord.ext import commands

from googletrans import Translator
from aiohttp import ClientSession
from naomi_paginator import Paginator
from humanize import fractional
from random import choice, randint, shuffle

import urllib.parse

class Image_tools(commands.Cog):
    def __init__(self, bot):
        """Команды для работы с цветами и изображениями"""
        self.bot = bot

    @commands.command(aliases=["ss"])
    @commands.cooldown(1, 8, commands.BucketType.member)
    @commands.is_nsfw()
    async def snapshot(self, ctx, *, url: str):
        """Сделать скриншот сайта

        ``ss google.com``
        """
        embeds = {
            'waiting': discord.Embed(
                color=discord.Colour.gold(),
                title = 'Ожидаем ответ от API',
                url = 'https://github.com/Naomi-Bot-Open-Source/ChromeChain/'),

            'error': discord.Embed(
                color=discord.Colour.dark_red(),
                title = 'Ошибка.'),

            'success': lambda image: 
                discord.Embed(
                    color = randint(0x000000, 0xFFFFFF)
                ).set_image(url=image)
            }

        msg = await ctx.send(embed=embeds['waiting'])

        async with ClientSession() as session:
            async with session.get(f"https://chromechain.herokuapp.com/?url={url}") as response:
                if response.status == 500:
                    ctx.command.reset_cooldown(ctx)
                    return await msg.edit(embed=embeds['error'], delete_after=60)
                await msg.edit(embed=embeds['success'](response.url))
            await session.close()
            
            

    @commands.command(aliases=["mcskin", "minecraftskin"])
    @commands.cooldown(1, 5, commands.BucketType.member)
    async def skin(self, ctx, nickname: str):
        """Получить скин игрока. (Minecraft)

        Можно использовать как ник, так и UUID игрока.

        ``skin TuxLabore``
        ``skin e458d85f78af422f889226daaabf35ce``"""

        emb = discord.Embed(
            title=f"Скин игрока {nickname}",
            url=f"https://mc-heads.net/body/{nickname}/600")
        emb.set_image(url=f"https://mc-heads.net/body/{nickname}/600")
        emb.set_author(
            name=ctx.message.author.name, 
            icon_url=str(ctx.author.avatar_url))
        emb.set_footer(text=f"{ctx.prefix}{ctx.command}")
        
        await ctx.send(embed=emb)

class Text_tools(commands.Cog):
    """Команды для работы с текстом
    Комманды в этой категории обрабатывают текст."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        aliases=[
            "textFormat",
            "textFormating",
            "title",
            "upper",
            "lower",
            "uppercase",
            "lowercase",
            "len",
            "length"])
    async def formatText(self, ctx, *, text: str):
        """Форматирование текста различными способами"""

        if len(text) > 751:
            return await ctx.send("> Текст должен быть не больше 750 символов")

        embed = discord.Embed(
            title="Форматирование текста", color=discord.Colour.purple())
        embed.set_author(
            name=ctx.message.author.name, icon_url=str(ctx.author.avatar_url))
        embed.set_footer(text=f"{ctx.prefix}{ctx.command}")

        embed.add_field(
            inline=False,
            name="Слова начинаються с заглавных букв",
            value=f"```{text.title()}```")
        embed.add_field(
            inline=False,
            name="Все буквы стают верхнего регистра",
            value=f"```{text.upper()}```")
        embed.add_field(
            inline=False,
            name="Все буквы стают нижнего регистра",
            value=f"```{text.lower()}```")
        embed.add_field(
            inline=False,
            name="Все буквы стают противополонжного регистра",
            value=f"```{text.swapcase()}```")
        embed.add_field(
            inline=False,
            name="Все буквы идут в обратном порядке",
            value=f"```{text[::-1]}```")
        embed.add_field(inline=False, name="Длина текста", value=f"```{len(text)}```")

        await ctx.send(embed=embed)

    @commands.command(aliases=["tl"])
    async def translate(self, ctx, lang, *, text):
        """Бот любезно переведёт текст который вы ему предоставили.
        Используется Google Translate

        Пример: `translate en Ваш текст тут`"""

        tl = Translator()

        try:
            tl = tl.translate(text, dest=lang)

            emb = discord.Embed(
                title="Перевести текст.",
                description=f"{tl.src.upper()} ```{text}``` {tl.dest.upper()}```{tl.text}```",
                color=discord.Colour.dark_blue(),
            )
            emb.set_author(
                name=ctx.message.author.name, icon_url=str(ctx.author.avatar_url)
            )
            emb.set_footer(text=f"{ctx.prefix}{ctx.command}")

            await ctx.send(embed=emb)

        except ValueError:
            emb = discord.Embed(
                title="Ошибка. Неправильный язык",
                description=f"Используйте `{ctx.prefix}translate <язык> <Ваш текст>`. Пример `{ctx.prefix}translate ja Якесь речення`",
                color=discord.Colour.red())
            emb.set_author(
                name=ctx.message.author.name, 
                icon_url=str(ctx.author.avatar_url))
            emb.set_footer(text=f"{ctx.prefix}{ctx.command}")

            await ctx.send(embed=emb)


class Number_tools(commands.Cog):
    def __init__(self, bot):
        """Команды по работе с числами"""
        self.bot = bot

    @commands.command(aliases=["calc", "expr", "expression"])
    async def calculate(self, ctx, *, raw_expression):
        """Математические обчисления с помощью API https://api.mathjs.org

        Пример: `calc 7 ^ 2 * 4 + 2` -> Результат: `198`"""
        expression = urllib.parse.quote(raw_expression.replace('**','^'))
        
        async with ClientSession() as session:
            async with session.get(
                f"http://api.mathjs.org/v4/?expr={expression}"
            ) as response:
                emb = discord.Embed(
                    title="Обчислить значение",
                    description=f"Результат обчисления ```{await response.text()}```",
                    color=discord.Colour.gold())
                emb.set_author(name=ctx.message.author.name, 
                    icon_url=str(ctx.author.avatar_url))
                emb.set_footer(text=f"{ctx.prefix}{ctx.command} | https://api.mathjs.org")
            
            await session.close()
        
        await ctx.send(embed=emb)

    @commands.command(
        aliases=[
            "advancedFloat",
            "convertFloat",
            "cf",
            "convert_float",
            "deciminalToFloat"])
    async def advFloat(self, ctx, raw: float):
        """Превращение десятичных дробей в обычные дроби

        Пример: `convertFloat 1.3939393939393939` (1.(39)) -> `1 13/33`
        """
        result = fractional(raw)
        emb = discord.Embed(
            title="Превратить десятичное число в обычную дробь",
            description=f"Превращённое число ```{result}```",
            color=discord.Colour.gold())
        emb.set_author(name=ctx.message.author.name, 
            icon_url=str(ctx.author.avatar_url))
        emb.set_footer(text=f"{ctx.prefix}{ctx.command}")
        
        await ctx.send(embed=emb)

class User_tools(commands.Cog):
    def __init__(self, bot):
        """Команды по работе с пользователями"""
        self.bot = bot

    @commands.command(
        aliases=["randM", "randomMem", "giveawayNow", "randMember", "rMember", "rm"])
    @commands.guild_only()
    async def randomMember(self, ctx, *, item):
        """Выбирает случайного победителя среди участников сервера."""
        memberList = [member.mention for member in ctx.guild.members if not member.bot]
        winner = choice(memberList)

        emb = discord.Embed(
            description=f"{winner} получает {item} от {ctx.author.mention}")
        emb.set_author(name=ctx.message.author.name, 
            icon_url=str(ctx.author.avatar_url))
        emb.set_footer(text=f"{ctx.prefix}{ctx.command}")
        
        await ctx.send(embed=emb)

    @commands.command(aliases=["myDiscriminator"], enabled=False)
    async def mytag(self, ctx):
        """Ники пользователей который имеют такой же дискриминатор как и у вас

        Сменив ваш ник на один из таких ваш дискриминатор сменится на случайный
        :warning: Discord устанавливает ограничения на смену ника и дискриминатора при нескольких использованиях"""
        names = [
            user.name
            for user in self.bot.users
            if user.name != ctx.author.name
            and ctx.author.discriminator == user.discriminator
        ]
        shuffle(names)

        if len(names) > 100:
            names = names[:100]
        if len(names) == 0:
            return await ctx.send(
                ":no_entry: Нам не удалось найти кого либо с таким же дискриминатором как у вас"
            )

        p = Paginator(ctx)

        for name in names:
            p.add_page(
                discord.Embed(
                    title=name, color=randint(0x000000, 0xFFFFFF)
                ).set_footer(
                    text="Смена вашего ника на какой либо из представленных повлечёт смену "
                    f"вашего дискриминатора ({ctx.author.discriminator}) на случайный"
                )
            )

        await p.call_controller()

def setup(bot):
    cogs = (Image_tools, Text_tools, Number_tools, User_tools)
    for cog in cogs:
        bot.add_cog(cog(bot))
