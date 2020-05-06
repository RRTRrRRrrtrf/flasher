import traceback
import sys, hashlib
from discord.ext import commands
import discord
import datetime as dt

class CommandErrorHandler(commands.Cog):
    """Error handler"""
    def __init__(self, bot):
        self.bot = bot
        self.perm_tl = {'add_reactions': 'Добавить новые реакции.',
                          'administrator': 'Администратор.',
                          'attach_files': 'Прикрепление файлов.',
                          'ban_members': 'Блокировка пользователей.',
                          'change_nickname': 'Смена никнейма.',
                          'connect': 'Подключение к голосовому каналу.',
                          'create_instant_invite': 'Создать приглашение.',
                          'deafen_members': 'Deafen members.',
                          'embed_links': 'Использовать ссылки.',
                          'external_emojis': 'Использовать емодзи других серверов.',
                          'kick_members': 'Выгнать пользователей.',
                          'manage_channels': 'Управление каналами.',
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
                await ctx.send(embed=discord.Embed(timestamp=ctx.message.created_at, 
                    description=':warning: Эта команда не может быть выполнена в личнных сообщениях.', 
                    color=discord.Colour.dark_red()).set_footer(text=self.bot.user.name))
                return

            elif isinstance(error, commands.BadArgument):
                ctx.command.reset_cooldown(ctx)
                await ctx.invoke(self.bot.get_command("help"), command=str(ctx.command))
                return

            elif isinstance(error, commands.UserInputError):
                ctx.command.reset_cooldown(ctx)
                await ctx.invoke(self.bot.get_command("help"), command=str(ctx.command))
                return

            elif isinstance(error, commands.NotOwner):

                await ctx.send(embed=discord.Embed(timestamp=ctx.message.created_at, 
                    description=':warning: Эта команда может быть исполнена только владельцем бота.', 
                    color=discord.Colour.dark_red()).set_footer(text=self.bot.user.name))
                return

            elif isinstance(error, commands.errors.CommandOnCooldown):
                await ctx.send(embed=discord.Embed(timestamp=ctx.message.created_at,
                    description=f':clock: Эту комманду нельзя использовать так часто!',#{retry_after.split(".")[0]}.',
                    color=discord.Colour.dark_red()).set_footer(text=self.bot.user.name))
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
                await ctx.send(embed=discord.Embed(timestamp=ctx.message.created_at, 
                    title=f'Для исполнения этой комманды вы должны обладать следующими правами:', 
                    description=f'```md\n{perms}\n```', 
                    color=discord.Colour.dark_red()).set_footer(text=self.bot.user.name))
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

                await ctx.send(embed=discord.Embed(timestamp=ctx.message.created_at, 
                    title=f'У вас нет ни одной из ниже указанных ролей для выполнения команды `{ctx.command}`:', 
                    description=f'```md\n{roles}\n```',
                    color=discord.Colour.dark_red()).set_footer(text=self.bot.user.name))
                return

            elif isinstance(error, commands.MissingRole):
                await ctx.send(embed=discord.Embed(timestamp=ctx.message.created_at,
                    description=f'У вас нет роли `{error.missing_role}` для выполнения этой команды', 
                    color=discord.Colour.dark_red()).set_footer(text=self.bot.user.name))
                return

            elif isinstance(error, commands.NSFWChannelRequired):
                await ctx.send(embed=discord.Embed(timestamp=ctx.message.created_at, 
                    description=f'Эту комманду можно исполнять только в канале с пометкой NSFW', 
                    color=discord.Colour.red()).set_footer(text=self.bot.user.name))
                return

            elif isinstance(error, discord.Forbidden):
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

                await ctx.send(embed=discord.Embed(timestamp=ctx.message.created_at, 
                    title=f'Боту должны быть предоставлены следующие права для выполнения этой команды:', 
                    description=f'```md\n{strperms}\n```', color=discord.Colour.dark_red()).set_footer(text=self.bot.user.name))
                return

        chn = await self.bot.read_json('config.json')
        err = "\n".join(traceback.format_exception(type(error), error, error.__traceback__))
        chn = await self.bot.fetch_channel(chn['bug report channel'])
        
        try: 
            await chn.send(embed=discord.Embed(title='Вызвана ошибка', 
                description=f'''Комманда: `{ctx.command}`
                Вызвана в: {ctx.channel} (вызвана {ctx.author})
            
                Сообщение: ```\n{ctx.message.content}\n```\nКод ошибки:\n```py\n{err}\n```''').set_footer(text=f'Ray ID: {hashlib.md5(bytes(err, "utf8")).hexdigest()}'))
        finally: 
            try: await ctx.send(embed=discord.Embed(title='Кажется я состолкнулся с ошибкой', 
            description=f'Если вы считаете что эта ошибка важная свяжитесь с разработчиком.\n```py\n{err}```', 
            color=discord.Colour.dark_red()))
            finally: pass 
    

def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))