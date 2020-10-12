import discord
from discord.ext import commands
from naomi_paginator import Paginator
from asyncio import sleep
from random import randint

class Info(commands.Cog):
    def __init__(self, bot):
        """Информация о боте"""
        self.bot = bot

    @commands.command(aliases=["links", "inv", "git", "github", "support", "supportServer"])
    async def invite(self, ctx):
        """Пригласите бота на ваш сервер"""

        invite = lambda code: discord.utils.oauth_url(self.bot.user.id, discord.Permissions(code)) # code variable receives int for permissions value

        emb = discord.Embed(
            title="Кастомизируйте права бота",
            description=f"[Приглашение со всеми возможными правами]({invite(-1)})",
            color=discord.Colour.gold())

        emb.add_field(
            name="Пригласите бота без прав",
            value=f"[Бот не создаст свою личную роль]({invite(0)})",
            inline=False)
        
        emb.add_field(
            name="Пригласите бота с правами администратора",
            value=f"[Бот будет иметь права администратора]({invite(8)})",
            inline=False)

        invite = self.bot.config.get('supportServerInvite')
        donate = self.bot.config.get('donationURL')

        emb.add_field(
            name="Другие ссылки",
            value=f"[Посетите сервер поддержки бота]({invite})\n"
            "[GitHub репозиторий бота](https://github.com/tuxlabore/flasher)\n"
            f"[Пожертвования]({donate})",
            inline=False)

        emb.set_footer(text=f"{ctx.prefix}{ctx.command}")

        await ctx.send(embed=emb)


    @commands.command(name="help", aliases=["commands", "cmds"])
    async def help(self, ctx, *, command: str = None):
        """Справочник по командам."""
        if command:   
            cmd = self.bot.get_command(command)
            if not cmd:                                                                             # If bot.get_command cannot found command it returns None
                notFoundEmbed = discord.Embed(title=f'Нам не удалось найти комманду {ctx.prefix}{command}',
                    color=discord.Colour.dark_red())    

                notFoundEmbed.set_footer(text=f'{ctx.prefix}{ctx.command} - {ctx.command.help}') # i'm so lazy for copy-paste description

                return await ctx.send(embed=notFoundEmbed, 
                                      delete_after=10)

            commandEmbed = discord.Embed(title=f'{ctx.prefix}{cmd.qualified_name} {cmd.signature}',       # outputs something like f.help <command> 
                                         description=cmd.help or 'Описание не предоставлено')
            commandEmbed.set_footer(text=f'{ctx.prefix}{ctx.command}', icon_url=ctx.author.avatar_url)

            if cmd.aliases:
                aliases = ','.join(cmd.aliases)
                commandEmbed.add_field(name='Варианты использования',      # f.help command -> 'commands, cmds' (string)
                                       value=aliases, inline=False)

            if type(cmd) is commands.Group:
                subCmds = cmd.commands
                subCmds = ', '.join([command.name for command in subCmds]) # f.prefix command -> 'self, guild' (string)
                commandEmbed.add_field(name='Подкоманды', 
                                       value=subCmds)

            return await ctx.send(embed=commandEmbed, delete_after=120)

        p = Paginator(ctx) # naomi_paginator init, here starts answer if command arg not provided        
        i = 0
        skipped = 0
        cogs = []

        for cog_name in self.bot.cogs:  # self.bot.cogs returns list with strings
            cog = self.bot.get_cog(cog_name)
            cogs.append(cog)

        for cog in cogs:
            
            doc = cog.__class__.__init__.__doc__

            cog_name = doc if doc else cog.__class__.__doc__.partition('\n')[0] # else block used in non-flasher cogs like jishaku
            
            cmds = [cmd.name 
                   for cmd in self.bot.commands 
                   if not cmd.hidden 
                   and cmd.cog_name is cog.__class__.__name__]

            
            if not cmds:        # [] case
                skipped += 1        
                continue

            i += 1

            cmds = [f'`{cmd}`' for cmd in cmds]
            cmds = ', '.join(cmds)

            embedPage = discord.Embed(title=ctx.command.help,
                                      color=randint(0x000000, 0xFFFFFF),
                                      timestamp=ctx.message.created_at)
            embedPage.add_field(name=cog_name,
                                value=cmds,)
            embedPage.set_thumbnail(url=self.bot.user.avatar_url)
            embedPage.set_footer(text=f'{ctx.prefix}{ctx.command} [команда] для более подробной информации',
                                 icon_url=ctx.author.avatar_url)
            
            p.add_page(embedPage)
        
        await p.call_controller()    






    @commands.command(aliases=["🏓", "pong", "latency"])
    async def ping(self, ctx):
        await ctx.send(f":ping_pong: {round(self.bot.latency * 1000)}ms")

def setup(bot):
    cog = Info(bot)
    bot.add_cog(cog)  