import discord
from discord.ext import commands
import random
import json
import os
from googletrans import Translator
from naomi_paginator import Paginator
import asyncio
from utils.errors import (TooManyTries, CanceledByUser) 
import time
import datetime



data = json.loads(open('data.json', 'r').read())
class Text_tools(commands.Cog):
    """Команды для работы с текстом
    Комманды в этой категории обрабатывают текст."""

    def __init__(self,bot):
        self.bot = bot
      
    @commands.command(aliases=['textFormat','textFormating'])
    async def formatText(self,ctx,*,text: str):
        '''Форматирование текста различными способами
        '''

        embed=discord.Embed(title='Форматирование текста',
            color=discord.Colour.purple())
        embed.set_author(name=ctx.message.author.name, 
            icon_url= str(ctx.author.avatar_url))
        embed.set_footer(text=f'{ctx.prefix}{ctx.command}')
        embed.add_field(inline=False,name='Слова начинаються с заглавных букв', value=f'```{text.title()}```')
        embed.add_field(inline=False,name='Все буквы стают верхнего регистра', value=f'```{text.upper()}```')
        embed.add_field(inline=False,name='Все буквы стают нижнего регистра', value=f'```{text.lower()}```')
        embed.add_field(inline=False,name='Все буквы стают противополонжного регистра',value=f'```{text.swapcase()}```')
        await ctx.send(embed=embed)


    @commands.command(aliases=['suggestIdea','bug','idea'])
    @commands.cooldown(1,60,commands.BucketType.user)
    async def suggest(self,ctx):
        f'''Подайте идею для бота
        '''

        def check(msg: discord.Message):
            return msg.author.id == ctx.author.id

        for i in range(5): 
            botMSG = await ctx.send('Введите тему идеи (не больше 60 символов).\n'
                           'Отправьте "Отмена" что бы отменить подачу идеи\n'
                           'или на "Пропустить" что бы не подавать тему для идеи\n')
            msg = await self.bot.wait_for('message',check=check, timeout=60)

            topic = msg.content
            try: await msg.delete()
            except: pass

            if topic.lower() in ('skip','пропустить','пропуск'):
                topic = None
                break
            elif topic.lower() in ('отмена','отменить','cancel'):
                raise CanceledByUser()

            if len(topic) < 61:
                await botMSG.delete()
                break
            if i == 4:
                raise TooManyTries()


        for i in range(5): 
            botMSG = await ctx.send('Введите описание идеи (не больше 512 символов).\n'
                                    'Отправьте "Отмена" что бы отменить подачу идеи\n')
            msg = await self.bot.wait_for('message',check=check, timeout=60)

            description = msg.content
            try: await msg.delete()
            except: pass

            if topic.lower() in ('отмена','отменить','cancel'):
                raise CanceledByUser()
            if len(topic) < 61:
                await botMSG.delete()
                break
            if i == 4:
                raise TooManyTries()            

        idea_number = len(await self.bot.sql('SELECT * FROM ideas;',parse=True)) + 1
        await self.bot.sql(f'INSERT INTO ideas (topic,description,author,time) VALUES ($1,$2,$3,$4)',
            topic,   description,   ctx.author.id,  int(time.time()))

        if not topic: topic = 'Тема не была установлена'

        channel = await self.bot.fetch_channel(self.bot.config['ideaChannel'])

        embed = discord.Embed(title=f'Идея #{idea_number} от {ctx.author.name} • {topic}',
            description=description,
            timestamp=datetime.datetime.now())
        embed.set_author(name=ctx.message.author.name,icon_url= str(ctx.author.avatar_url))
        embed.set_footer(text='Идея была подана')

        await channel.send(embed=embed)

        embed = discord.Embed(title=f'Ваша идея #{idea_number} отправлена успешно',
            color=discord.Colour.green(),
            url=self.bot.config["supportServerInvite"])
        embed.add_field(name=topic,
            value=description)

        await ctx.send(embed=embed)
        
    @commands.command(hidden=True)
    @commands.is_owner()
    async def msg(self,ctx,*,textArg):
        '''Отправить сообщение от имени бота

        '''
    
        await ctx.send(textArg.replace(r' \ ',''))
        try:await ctx.message.delete()
        except:pass



    @commands.command(aliases=['tl'])
    async def translate(self,ctx,lang,*,text):
        """Бот любезно переведёт текст который вы ему предоставили.
        Используется Google Translate
            
        Пример: `f.translate en Ваш текст тут`"""

        tl = Translator()
        
        try:
            tl = tl.translate(text,dest=lang)
    
            emb = discord.Embed(title='Перевести текст.',
                description=f'{tl.src.upper()} ```{text}``` {tl.dest.upper()}```{tl.text}```',
                color=discord.Colour.dark_blue())
            emb.set_author(name=ctx.message.author.name, 
                icon_url= str(ctx.author.avatar_url))
            emb.set_footer(text=f'{ctx.prefix}{ctx.command}')
            
            await ctx.send(embed=emb)
            
        except ValueError:
            emb = discord.Embed(title='Ошибка. Неправильный язык',
                description=f'Используйте `/translate <язык> <Ваш текст>`. Пример `/translate ja Мова солов\'їна`',
                color=discord.Colour.red())
            emb.set_author(name=ctx.message.author.name, 
                icon_url= str(ctx.author.avatar_url))
            emb.set_footer(text=f'{ctx.prefix}{ctx.command}')
            
            await ctx.send(embed=emb)                   
                


    @commands.command()
    async def passGen(self,ctx,howmany: int,lengs: int):
        """Генератор паролей.

        Пример: `f.passGen 10 16` - сгенерируется 10 паролей длиной 16 символов
        :warning: В целях предотвращения крашей бота установлен лимит: максимальное количество паролей - 49, а макс. длина - 24."""

        if howmany < 50 and lengs < 25: 

            a = ''
            b = ''

            for i in range(howmany):
                i = i # Проигнорируйте эту строку, просто что бы линтер не ругался
                for i in range(lengs): a += random.choice('1234567890QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm')
                b += '> ' + a + '\n'
                a = ''

            await ctx.send(f'{b}\nСгенерировано {howmany} паролей длинной {lengs} символов.')

        else:
            await ctx.send(f'> Ошибка. Значения слишком большие.\n> Максимальное количество - 49, максимальная длина - 24')



    @commands.command(hidden=True)
    async def genAd(self,ctx):
        """Как вам удалось найти наш генератор рекламы?"""

        column1 = random.choice(['Только','Ура!','Внимание!','Наконецто:','Это оно!','Поспеши!'])
        column2 = random.choice(['Ждя тебя','Для твоей семьи','Для женщин','Для детей','Для мужчин','Для бабулек под подъездом','Для кота'])
        column3 = random.choice(['сегодня','завтра','действительно никогда','этой пятницы','в твоем коте','в будние дни','в часы когда именно тебе везти не будет'])
        column4 = random.choice(['лучшая','никому не нужная','уникальная','безпроиграшная','долгожданная','сезонная','доступная'])
        column5 = random.choice(['скидка','предложение','тварь блохастая','акция','выгода','цена'])
        column6 = random.choice(['50кот-процентов.','2 за ценой кота.','1 + 1 = -1.','на всё.','1999.99 руб.','99 руб','каждый десятый проезд в трамваее с 5:00 по 7:00 беспатный!'])
        column7 = random.choice(['Не пропускай!','Не прогуливай уроки!','Выбери нас!','Не жди!','Будь сожраный львом!','Успей!','Получи ляща по лицу!'])
        
        await ctx.send(f'> **{column1} {column2} {column3} {column4} {column5} {column6} {column7}**\n Для <@{ctx.author.id}>')



    @commands.command(aliases=['db'])
    async def dashboard(self,ctx,id :int=0):
        """Просмотр информации про бота
        
        Пример: `f.dashboard 12` покажет запись с ID 12
        `f.dashboard` покажет последнюю запись"""
        data = await self.bot.read_json('data.json')
        data = data['dashboard']
        p = Paginator(ctx)
        
        if id and not data[str(id)]: return

        for key in {key: data[key] for key in list(data.keys())[::-1]}:
            values = data[key]
            p.add_page(discord.Embed(title=values['name'],
                description=values['value'],
                color=random.randint(0x000000,0xFFFFFF)))
        
        await p.call_controller(start_page=id)


    @commands.command(aliases=['dashboardAdd','dbAdd','addDb'],hidden=True)
    @commands.is_owner()
    async def addDashboard(self,ctx,*,content):
        """Добавить запись в Dashboard"""
        dd = data['dashboard']

        id = str(int(list(dd)[-1]) + 1)

        dd[id] = {'name':f'ID: {id}, Author: {ctx.author.name}',"value":content}
        chn = await self.bot.fetch_channel(self.bot.config["dashboardChannel"])
        
        emb = discord.Embed(description=f'Новая запись в Dashboard')
        emb.add_field(name=f'ID: {id}',value=content)
        emb.set_author(name=ctx.message.author.name, icon_url= str(ctx.author.avatar_url))
        emb.set_footer(text=f'{ctx.prefix}{ctx.command}')
        await chn.send(embed=emb)
        
        await self.bot.write_json('data.json',data)

        await ctx.send('> OK')



def setup(bot):
    bot.add_cog(Text_tools(bot))
