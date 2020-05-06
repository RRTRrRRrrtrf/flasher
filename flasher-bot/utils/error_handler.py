import traceback
import sys, hashlib
from discord.ext import commands
import discord
import datetime as dt

class CommandErrorHandler(commands.Cog):
    """Error handler"""
    def __init__(self, bot):
        self.bot = bot
        self.perm_tl = {'add_reactions': 'добавлять реакции',
                          'administrator': 'администратор',
                          'attach_files': 'прикреплять файлы',
                          'ban_members': 'банить пользователей',
                          'change_nickname': 'менять никнейм',
                          'connect': 'подключатся к голосовым каналам',
                          'create_instant_invite': 'создавать приглашение',
                          'deafen_members': 'мутить пользователей',
                          'embed_links': 'прикреплять ссылки',
                          'external_emojis': 'использовать глобальные эмодзи',
                          'kick_members': 'выгонять пользователей',
                          'manage_channels': 'управлять каналами',
                          'manage_emojis': 'управлять эмодзи',
                          'manage_guild': 'управлять сервером',
                          'manage_messages': 'управлять сообщениями',
                          'manage_nicknames': 'управлять никнеймами',
                          'manage_permissions': 'управлять правами',
                          'manage_roles': 'управлять ролями',
                          'manage_webhooks': 'управлять вебхуками',
                          'mention_everyone': 'упоминать всех',
                          'move_members': 'перемещать пользователей',
                          'mute_members': 'мутить пользователей',
                          'priority_speaker': 'прироритетный спикер',
                          'read_message_history': 'читать историю сообщений',
                          'read_messages': 'читать сообщения',
                          'send_messages': 'отправлять сообщения',
                          'send_tts_messages': 'отправлять TTS-сообщения',
                          'speak': 'использовать микрофон',
                          'stream': 'стримить',
                          'use_external_emojis': 'использовать глобальные эмодзи',
                          'use_voice_activation': 'использовать активацию по голосу',
                          'view_audit_log': 'просматривать журнал аудита',
                          'view_channel': 'просматривать каналы',
                          'view_guild_insights': 'view_guild_insights',
                          'voice': 'подключатся к голосовым каналам'}
        self.userToReport = None
        self.chnToReport = None














    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        if hasattr(ctx.command, 'on_error'):
            return
        
        ignored = (commands.CommandNotFound)
        ignored2 = (commands.BadArgument, commands.UserInputError)
        error = getattr(error, 'original', error)
        
        if isinstance(error, ignored):
            return
        else:
            if not isinstance(error, ignored2): 
                await ctx.message.add_reaction('🚫')

            if isinstance(error, commands.DisabledCommand):
                return

            elif isinstance(error, commands.NoPrivateMessage):
                await ctx.send(embed=discord.Embed(timestamp=ctx.message.created_at, title=f'Эта команда не может быть выполнена в ЛС.', color=discord.Colour.red()).set_footer(text=self.bot.user.name))
                return

            elif isinstance(error, commands.BadArgument):
                # await ctx.send(embed=discord.Embed(timestamp=ctx.message.created_at, title='Ошибка', description=f'You give me bad argument for command  `{ctx.command}`.', color=discord.Colour.red()).set_footer(text=self.bot.user.name))
                ctx.command.reset_cooldown(ctx)
                await ctx.invoke(self.bot.get_command("help"), command=str(ctx.command))
                return

            elif isinstance(error, commands.UserInputError):
                # await ctx.send(embed=discord.Embed(timestamp=ctx.message.created_at, title='Ошибка', description=f'You forgot to give me required arguments\nArguments for command `{ctx.command}`: {ctx.command.signature}', color=discord.Colour.red()).set_footer(text=self.bot.user.name))
                ctx.command.reset_cooldown(ctx)
                await ctx.invoke(self.bot.get_command("help"), command=str(ctx.command))
                return
            elif isinstance(error, commands.NotOwner):
                return
            elif isinstance(error, commands.errors.CommandOnCooldown):
                r = error.retry_after
                retry_after = str(dt.timedelta(seconds=int(r)))
                titles = {'lottery': 'Азартные игры это плохо, не играйте в них часто!', 'daily': 'Ежедневная степендия доступна только раз в сутки!'}
                title = 'Не так быстро!'
                if ctx.command.name in titles: title = titles[ctx.command.name]
                await ctx.send(embed=discord.Embed(timestamp=ctx.message.created_at, title=title, description=f'Подождите {retry_after.split(".")[0]} перед повторным использованием.', color=discord.Colour.red()).set_footer(text=self.bot.user.name))
                return
            elif isinstance(error, commands.errors.MissingPermissions):
                i = 0
                perms = []
                for perm in error.missing_perms:
                    i += 1
                    try: p = f'{i}. {self.perm_tl[perm]}'
                    except: p = f'{i}. {perm} (Translate is not yet completed)'
                    if i != len(error.missing_perms): p += ';'
                    perms.append(p)
                perms = '\n'.join(perms)
                await ctx.send(embed=discord.Embed(timestamp=ctx.message.created_at, title=f'У вас нет следующих прав для выполнения этой команды:', description=f'```md\n{perms}\n```', color=discord.Colour.red()).set_footer(text=self.bot.user.name))
                return
            elif isinstance(error, commands.MissingAnyRole):
                i = 0
                roles = []
                for role in error.missing_roles:
                    i += 1
                    r = f'{i}. {role}'
                    if i != len(error.missing_roles): r += ';'
                    roles.append(r)
                roles = '\n'.join(roles)
                await ctx.send(embed=discord.Embed(timestamp=ctx.message.created_at, title=f'У вас нет ни одной из ниже указанных ролей для выполнения команды `{ctx.command}`:', description=f'```md\n{roles}\n```', color=discord.Colour.red()).set_footer(text=self.bot.user.name))
                return
            elif isinstance(error, commands.MissingRole):
                await ctx.send(embed=discord.Embed(timestamp=ctx.message.created_at, title=f'У вас нет роли `{error.missing_role}` для выполнения этой команды', color=discord.Colour.red()).set_footer(text=self.bot.user.name))
                return
            elif isinstance(error, commands.NSFWChannelRequired):
                await ctx.send(embed=discord.Embed(timestamp=ctx.message.created_at, title=f'Эта команда может быть выполнена только в NSFW-канале', color=discord.Colour.red()).set_footer(text=self.bot.user.name))
                return
            elif isinstance(error, discord.Forbidden):
                if ctx.command.name in ('ban', 'kick'): return
                perms = discord.Permissions(error.code)
                needperms = [x for x in dir(perms) if not x.startswith('_') if getattr(perms, x) == True]
                strperms = []
                i = 0
                for perm in needperms:
                    i += 1
                    r = f'{i}. {perm}'
                    if i != len(needperms): r += ';'
                    strperms.append(r)
                strperms = '\n'.join(strperms)
                await ctx.send(embed=discord.Embed(timestamp=ctx.message.created_at, title=f'У меня нет следующих прав для выполнения этой команды:', description=f'```md\n{strperms}\n```', color=discord.Colour.red()).set_footer(text=self.bot.user.name))
                return
        user = await self.bot.read_json('config.json')
        chn = await self.bot.read_json('config.json')
        err = "\n".join(traceback.format_exception(type(error), error, error.__traceback__))
        user = await self.bot.fetch_user(user['bug report user'])
        chn = await self.bot.fetch_channel(chn['bug report channel'])
        try: await chn.send(embed=discord.Embed(title='SCBot Error', description=f'''Command: `{ctx.command}`\nCalled in: {ctx.channel} (called by {ctx.author})\n\nMessage: ```\n{ctx.message.content}\n```''').set_footer(text=f'Ray ID: {hashlib.md5(bytes(err, "utf8")).hexdigest()}'))
        finally: 
            try: await ctx.send(embed=discord.Embed(title='Произошла ошибка при выполнении команды, повторите позже.', description='Я отправил эту ошибку моему разработчику и он исправит её в скорое время!', color=discord.Colour.red()))
            finally: await user.send(f'Error with executing command {ctx.command}\nCalled by: {ctx.author}\nCalled in: {ctx.guild} > {ctx.channel}\nError: ```py\n{err}\n```')
    @commands.command(name='test-eh', hidden=True)
    @commands.is_owner()
    async def t(self, ctx):
        '''none'''
        ctx.goFuck

def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))