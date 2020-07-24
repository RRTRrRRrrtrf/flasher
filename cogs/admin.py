import discord
from discord.ext import commands
import jishaku
import os
import humanize
import datetime
import time



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
        requests = code.content.split(';')
        out = []
        line = 0
        returned = 'RESULT\n\n'
        
        for request in requests:
            if not request: # '' case
                continue
            
            try:
                answer = await self.bot.sql(request)
            
            except Exception as e:
                answer = f'{type(e).__name__}:  {e}'
            
            out.append(answer)
        
        for result in out:
            returned += f'Line {line}: ```{result}```\n\n'
            line += 1
        
        if len(returned) > 1997:
            returned = returned[:1997] + '...'
            
        await ctx.send(returned)
            
            
            
            
    @commands.command(hidden=True)
    async def sqlBackup(self,ctx):
        """Создать резервную копию базы данных"""
        os.system(f'pg_dump {self.bot.config["sqlPath"]} > backup.psql')
        
        await ctx.author.send(f'Backup loaded: ' + humanize.naturalsize(os.path.getsize('backup.psql')),
            file=discord.File('backup.psql'))
    
    
    
    @commands.command(hidden=True)
    async def msg(self,ctx,*,textArg):
        '''Отправить сообщение от имени бота'''
        await ctx.send(textArg)
        
        try:
            await ctx.message.delete()
        except:
            pass
    
    
    
    @commands.command(aliases=['dashboardAdd','dbAdd','addDb'],hidden=True)
    async def addDashboard(self,ctx):
        """Добавить запись в Dashboard"""
        def check(msg: discord.Message):
            return msg.author.id == ctx.author.id

        for i in range(5): 
            botMSG = await ctx.send('Введите тему записи (не больше 60 символов).\n'
                           'Отправьте "Отмена" что бы отменить подачу идеи\n')
            msg = await self.bot.wait_for('message',check=check, timeout=60)

            topic = msg.content
            try: await msg.delete()
            except: pass

            if topic.lower() in ('отмена','отменить','cancel'):
                raise CanceledByUser()
            
            if len(topic) < 61:
                await botMSG.delete()
                break
            if i == 4:
                raise TooManyTries()

        for i in range(5): 
            botMSG = await ctx.send('Введите описание записи (не больше 512 символов).\n'
                                    'Отправьте "Отмена" что бы отменить подачу идеи\n'
                                    'или "Пропустить" что бы не отправлять описание для записи\n')
            msg = await self.bot.wait_for('message',check=check, timeout=60)

            description = msg.content
            try: await msg.delete()
            except: pass

            if description.lower() in ('skip','пропустить','пропуск'):
                description = None
                break
            elif description.lower() in ('отмена','отменить','cancel'):
                raise CanceledByUser()

            if len(description) < 513:
                await botMSG.delete()
                break
            if i == 4:
                raise TooManyTries()            

        write_number = len(await self.bot.sql('SELECT * FROM dashboard')) + 1
        await self.bot.sql(f'INSERT INTO dashboard (author, topic, content, time) VALUES ($3,$1,$2,$4)',
            topic,   description,   ctx.author.id,  int(time.time()))

        if not topic: topic = 'Тема не была установлена'

        channel = await self.bot.fetch_channel(self.bot.config['dashboardChannel'])

        embed = discord.Embed(title=f'Запись #{write_number} от {ctx.author.name} • {topic}',
            description=description,
            timestamp=datetime.datetime.now())
        embed.set_author(name=ctx.message.author.name,icon_url= str(ctx.author.avatar_url))
        embed.set_footer(text='Запись опубликована')

        await channel.send(embed=embed)

        embed = discord.Embed(title=f'Ваша запись #{write_number} опубликована успешно',
            color=discord.Colour.green(),
            url=self.bot.config["supportServerInvite"])
        embed.add_field(name=topic,
            value=description)

        await ctx.send(embed=embed)

        


def setup(bot):
    cog = Admin(bot)
    bot.add_cog(cog)
    if not cog.bot.config['blacklistStatus']:
            cog.bot.remove_command('blacklistUser')
            cog.bot.remove_command('pardonUser')
