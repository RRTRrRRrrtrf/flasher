import discord
from discord.ext import commands
import jishaku
from naomi_paginator import Paginator
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

        try:
            outputs = []
            lineId = 0

            for line in code.content.split("\n"):
                if line.replace(" ", "") != "":

                    output = await self.bot.multisql(line)
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
    
    
    
    @commands.command(hidden=True)
    async def msg(self,ctx,*,textArg):
        '''Отправить сообщение от имени бота

        '''
    
        await ctx.send(textArg.replace(r' \ ',''))
        try:await ctx.message.delete()
        except:pass
    
    
    
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
