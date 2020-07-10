import discord
from discord.ext import commands
import jishaku
from naomi_paginator import Paginator
import os


class Admin(commands.Cog):
    """Комманды для владельца бота"""
    def __init__(self, bot):
        self.bot = bot
            
            
            
    async def cog_check(self, ctx):
        if await self.bot.is_owner(ctx.author):
            return True
        else:
            raise commands.NotOwner()
            
    
    @commands.command(hidden=True, aliases=['blacklist','bl','blU'])
    async def blacklistUser(self, ctx, id: int):
        """Добавить пользователя в ЧС бота."""
        await self.bot.sql(f'INSERT INTO blacklist VALUES ({id}) ON CONFLICT DO NOTHING;')
        await ctx.send("> OK")


    @commands.command(hidden=True, aliases=['pardon','unblacklist', 'unblacklistUser','ubl', 'ublU','pu'])
    async def pardonUser(self, ctx, id: int):
        """Исключить пользователя из ЧС бота."""
        await self.bot.sql(f'DELETE FROM blacklist WHERE id={id};')
        await ctx.send("> OK")
        
        
    @commands.command(name="sql", hidden=True)
    async def sql(self, ctx, *, code: jishaku.codeblocks.codeblock_converter):
        """Исполнить запрос к PostgreSQL"""

        try:
            outputs = []
            lineId = 0

            for line in code.content.split("\n"):
                if line.replace(" ", "") != "":

                    output = await self.bot.sql(line)
                    x = [str(dict(i)) for i in output]
                    out = ("\n".join(x) or "No output").replace("@", "@\u200b")
                    outputs.append(f"{lineId}: {out}")
                    lineId += 1

            out = "\n".join(outputs)

            if len(out) >= 1900:

                p = Paginator(ctx)
                pages = [out[i : i + 1900] for i in range(0, len(out), 1900)]
                for page in pages:
                    await p.add_page(discord.Embed(description=page))

                await p.call_controller()

            else:
                await ctx.send(out)
        except Exception as e:
            await ctx.send(f"{type(e).__name__}:  {e}")


    @commands.command(hidden=True)
    async def sqlBackup(self,ctx):
        """Создать резервную копию базы данных"""
        reporter = ctx.author
        os.system(f'pg_dump {self.bot.config["sqlPath"]} > backup.psql')
        await reporter.send(f'Backup loaded: ' + humanize.naturalsize(os.path.getsize('backup.psql')),
            file=discord.File('backup.psql'))
        


def setup(bot):
    cog = Admin(bot)
    bot.add_cog(cog)
    if not cog.bot.config['blacklistStatus']:
            cog.bot.remove_command('blacklistUser')
            cog.bot.remove_command('pardonUser')
