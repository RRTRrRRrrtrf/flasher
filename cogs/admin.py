import discord
from discord.ext import commands

import jishaku
import os
import sys
import humanize
import datetime
import time

from utils.db import SQL # pylint: disable=import-error

class Admin(commands.Cog):
    """Комманды для владельца бота"""

    def __init__(self, bot):
        self.bot = bot
        self.sql = SQL(bot.db).sql

    async def cog_check(self, ctx):
        if await self.bot.is_owner(ctx.author):
            return True
        else:
            raise commands.NotOwner()

    @commands.command(hidden=True, aliases=['reboot'])
    async def restart(self, ctx):
        await ctx.send('> Restart')
        os.execl(sys.executable, sys.executable, *sys.argv)

    @commands.command(hidden=True, aliases=["blacklist", "bl", "blU"])
    async def blacklistUser(self, ctx, id: int):
        """Добавить пользователя в ЧС бота."""
        await self.sql(
            f"INSERT INTO blacklist VALUES ({id}) ON CONFLICT DO NOTHING;"
        )
        await ctx.send("> OK")

    @commands.command(
        hidden=True,
        aliases=["pardon", "unblacklist", "unblacklistUser", "ubl", "ublU", "pu"],
    )
    async def pardonUser(self, ctx, id: int):
        """Исключить пользователя из ЧС бота."""
        await self.sql(f"DELETE FROM blacklist WHERE id={id};")
        await ctx.send("> OK")

    @commands.command(name="sql", hidden=True)
    async def sql_cmd(self, ctx, *, code: jishaku.codeblocks.codeblock_converter):
        """Исполнить запрос к PostgreSQL"""
        requests = code.content.split(";")
        out = []
        line = 0
        returned = "RESULT\n\n"

        for request in requests:
            if not request:  # '' case
                continue

            try:
                answer = await self.sql(request)

            except Exception as e:
                answer = f"{type(e).__name__}:  {e}"

            out.append(answer)

        for result in out:
            returned += f"Line {line}: ```{result}```\n\n"
            line += 1

        if len(returned) > 1997:
            returned = returned[:1997] + "..."

        await ctx.send(returned)

    @commands.command(hidden=True)
    async def sqlBackup(self, ctx):
        """Создать резервную копию базы данных"""
        os.system(f'pg_dump {self.bot.config["sqlPath"]} > backup.psql')

        await ctx.author.send(
            f"Backup loaded: " + humanize.naturalsize(os.path.getsize("backup.psql")),
            file=discord.File("backup.psql"))

    @commands.command(hidden=True)
    async def msg(self, ctx, *, textArg):
        """Отправить сообщение от имени бота"""
        await ctx.send(textArg)

        try:
            await ctx.message.delete()
        except:
            pass

    @commands.command(aliases=["dashboardAdd", "dbAdd", "addDb"], hidden=True)
    async def addDashboard(self, ctx, topic: str, *, description: str):
        """Добавить запись в Dashboard"""

        write_number = len(await self.sql("SELECT * FROM dashboard")) + 1
        await self.sql(
            f"INSERT INTO dashboard (author, topic, content, time) VALUES ($3,$1,$2,$4)",
            topic,
            description,
            ctx.author.id,
            int(time.time()),
        )

        if not topic:
            topic = "Тема не была установлена"

        channel = await self.bot.fetch_channel(self.bot.config["dashboardChannel"])

        embed = discord.Embed(
            title=f"Запись #{write_number} от {ctx.author.name} • {topic}",
            description=description,
            timestamp=datetime.datetime.now(),
        )
        embed.set_author(
            name=ctx.message.author.name, icon_url=str(ctx.author.avatar_url)
        )
        embed.set_footer(text="Запись опубликована")

        msg = await channel.send(embed=embed)

        if channel.is_news():
            await msg.publish()
        
        embed = discord.Embed(
            title=f"Ваша запись #{write_number} опубликована успешно",
            color=discord.Colour.green(),
            url=self.bot.config["supportServerInvite"],
        )
        embed.add_field(name=topic, value=description)

        await ctx.send(embed=embed)


def setup(bot):
    cog = Admin(bot)
    bot.add_cog(cog)

