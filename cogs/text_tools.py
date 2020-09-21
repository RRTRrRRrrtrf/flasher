import discord
from discord.ext import commands

from googletrans import Translator


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



def setup(bot):
    bot.add_cog(Text_tools(bot))
