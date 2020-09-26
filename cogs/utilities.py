import discord
from discord.ext import commands

from colormap import rgb2hex, rgb2hsv, hex2rgb
from googletrans import Translator
from aiohttp import ClientSession
from naomi_paginator import Paginator
from humanize import fractional

import urllib.parse
import time
import random


class Image_tools(commands.Cog):
    """Команды для работы с цветами и изображениями"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["ss"])
    @commands.cooldown(1, 8, commands.BucketType.member)
    @commands.is_nsfw()
    async def snapshot(self, ctx, *, url: str):
        """Сделать скриншот сайта

        ``/ss google.com``
        """
        msg = await ctx.send(
            embed=discord.Embed(
                title="Ожидаем ответ от API...", color=discord.Colour.light_grey()
            ))
        try:
            async with ClientSession() as session:
                async with session.get(
                    f"https://chromechain.herokuapp.com/?url={url}"
                ) as resp:
                    await msg.edit(
                        content=None,
                        embed=discord.Embed(
                            color=ctx.author.color, title=url
                        ).set_image(url=(await resp.json())["content"]),
                    )
            await session.close()
        except:
            ctx.command.reset_cooldown(ctx)
            await msg.edit(
                content=None,
                embed=discord.Embed(title="Ошибка.", color=discord.Colour.red()),
            )

    @commands.command(aliases=["mcskin", "minecraftskin"])
    @commands.cooldown(1, 5, commands.BucketType.member)
    async def skin(self, ctx, nickname: str):
        f"""Получить скин игрока. (Minecraft)

        Можно использовать как ник, так и UUID игрока.

        ``{ctx.prefix}skin TuxLabore``
        ``{ctx.prefix}skin e458d85f78af422f889226daaabf35ce``"""

        emb = discord.Embed(
            title=f"Скин игрока {nickname}",
            url=f"https://mc-heads.net/body/{nickname}/600",
        )
        emb.set_image(url=f"https://mc-heads.net/body/{nickname}/600")
        emb.set_author(
            name=ctx.message.author.name, icon_url=str(ctx.author.avatar_url)
        )
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
            "length",
        ]
    )
    async def formatText(self, ctx, *, text: str):
        """Форматирование текста различными способами"""

        if len(text) > 751:
            return await ctx.send("> Текст должен быть не больше 750 символов")

        embed = discord.Embed(
            title="Форматирование текста", color=discord.Colour.purple()
        )
        embed.set_author(
            name=ctx.message.author.name, icon_url=str(ctx.author.avatar_url)
        )
        embed.set_footer(text=f"{ctx.prefix}{ctx.command}")

        embed.add_field(
            inline=False,
            name="Слова начинаються с заглавных букв",
            value=f"```{text.title()}```",
        )
        embed.add_field(
            inline=False,
            name="Все буквы стают верхнего регистра",
            value=f"```{text.upper()}```",
        )
        embed.add_field(
            inline=False,
            name="Все буквы стают нижнего регистра",
            value=f"```{text.lower()}```",
        )
        embed.add_field(
            inline=False,
            name="Все буквы стают противополонжного регистра",
            value=f"```{text.swapcase()}```",
        )
        embed.add_field(
            inline=False,
            name="Все буквы идут в обратном порядке",
            value=f"```{text[::-1]}```",
        )
        embed.add_field(inline=False, name="Длина текста", value=f"```{len(text)}```")

        await ctx.send(embed=embed)

    @commands.command(aliases=["tl"])
    async def translate(self, ctx, lang, *, text):
        """Бот любезно переведёт текст который вы ему предоставили.
        Используется Google Translate

        Пример: `f.translate en Ваш текст тут`"""

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
                description=f"Используйте `/translate <язык> <Ваш текст>`. Пример `/translate ja Мова солов'їна`",
                color=discord.Colour.red(),
            )
            emb.set_author(
                name=ctx.message.author.name, icon_url=str(ctx.author.avatar_url)
            )
            emb.set_footer(text=f"{ctx.prefix}{ctx.command}")

            await ctx.send(embed=emb)


class Number_tools(commands.Cog):
    """Команды по работе с числами"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["calc", "expr", "expresion"])
    async def calculate(self, ctx, *, toCalc):
        """Математические обчисления с помощью API https://api.mathjs.org

        Пример: `/calc sqr(7)*4+2` -> `((7^2) * 4) +2` -> Результат: `198`

        """
        async with ClientSession() as session:
            async with session.get(
                f"http://api.mathjs.org/v4/?expr={urllib.parse.quote(toCalc.replace('**','^'))}"
            ) as response:
                emb = discord.Embed(
                    title="Обчислить значение",
                    description=f"Результат обчисления ```{await response.text()}```",
                    color=discord.Colour.gold(),
                )
                emb.set_author(
                    name=ctx.message.author.name, icon_url=str(ctx.author.avatar_url)
                )
                emb.set_footer(
                    text=f"{ctx.prefix}{ctx.command} | https://api.mathjs.org"
                )
            await session.close()
        await ctx.send(embed=emb)

    @commands.command(
        aliases=[
            "advancedFloat",
            "convertFloat",
            "cf",
            "convert_float",
            "deciminalToFloat",
        ]
    )
    async def advFloat(self, ctx, toNat: float):
        """Превращение десятичных дробей в обычные дроби

        Пример: `/convertFloat 1.3939393939393939` (1.(39)) -> `1 13/33`
        """
        toNat = fractional(toNat)
        emb = discord.Embed(
            title="Превратить десятичное число в обычную дробь",
            description=f"Превращённое число ```{toNat}```",
            color=discord.Colour.gold(),
        )
        emb.set_author(
            name=ctx.message.author.name, icon_url=str(ctx.author.avatar_url)
        )
        emb.set_footer(text=f"{ctx.prefix}{ctx.command}")
        await ctx.send(embed=emb)

class User_tools(commands.Cog):
    """Команды по работе с пользователями"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        aliases=["randM", "randomNem", "giveawayNow", "randMember", "rMember", "rm"]
    )
    async def randomMember(self, ctx, *, textArg):
        memberList = []
        for m in ctx.guild.members:
            if not m.bot:
                memberList.append(m.id)

        emb = discord.Embed(
            description=f"<@{random.choice(memberList)}> получает {textArg} от <@{ctx.author.id}>"
        )
        emb.set_author(
            name=ctx.message.author.name, icon_url=str(ctx.author.avatar_url)
        )
        emb.set_footer(text=f"{ctx.prefix}{ctx.command}")
        await ctx.send(embed=emb)

    @commands.command(aliases=["myDiscriminator"])
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
        random.shuffle(names)

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
                    title=name, color=random.randint(0x000000, 0xFFFFFF)
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
