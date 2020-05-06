import discord
from discord.ext import commands
import time
import random
import json
import os
from googletrans import Translator
#import emoji


data = json.loads(open('data.json', 'r').read())
class text_tools(commands.Cog):

    def __init__(self,bot):
        self.bot = bot
      


    @commands.command(aliases=['capitalize','capitalizeWord','capitalizeEveryWord','title'])                # Пример Для Вас
    async def capitalize_every_word(self,ctx, *, textArg):
        '''Все слова начинаються с заглавной буквы.

        Пример: `/title aBCD` -> `Abcd`
        '''
        embed=discord.Embed(description=f'```{textArg.title()}```')
        embed.set_author(name=ctx.message.author.name, 
            icon_url= str(ctx.author.avatar_url))
        embed.set_footer(text=f'{ctx.prefix}{ctx.command}')

        await ctx.send(embed=embed)



    @commands.command(aliases=['upper','uppercasewords','uppercaseword'])                           # ПРИМЕР ДЛЯ ВАС
    async def uppercase(self,ctx, *, textArg):
        '''Все буквы стают верхнего регистра

        Пример: `/uppercase abcD` -> `ABCD`
        '''
        embed=discord.Embed(description=f'```{textArg.upper()}```')
        embed.set_author(name=ctx.message.author.name, 
            icon_url= str(ctx.author.avatar_url))
        embed.set_footer(text=f'{ctx.prefix}{ctx.command}')

        await ctx.send(embed=embed)



    @commands.command(aliases=['lower','lowerwords','lowercasewords'])                              # пример для вас
    async def lowercase(self,ctx, *, textArg):
        '''Все слова стают нижнего регистра

        Пример: `/lowercase ABCd` -> `abcd`
        '''

        embed=discord.Embed(description=f'```{textArg.lower()}```')
        embed.set_author(name=ctx.message.author.name, 
            icon_url= str(ctx.author.avatar_url))
        embed.set_footer(text=f'{ctx.prefix}{ctx.command}')

        await ctx.send(embed=embed)



    @commands.command(aliases=['suggestIdea','bug','idea'])
    async def suggest(self,ctx,*,textArg):
        '''Подайте идею для бота
        Пример: `/idea Скриншот сайтов`
        '''
        chn = await self.bot.read_json('config.json')
        chn = await self.bot.fetch_channel(chn["idea channel"])

        emb = discord.Embed(description=f'Идея {data["idea"]} от {ctx.author.name}#{ctx.author.discriminator} ({ctx.author.id}) ')

        emb.add_field(name='Поступившая идея',
            value=textArg)
        emb.set_author(name=ctx.message.author.name, 
            icon_url= str(ctx.author.avatar_url))
        emb.set_footer(text=f'{ctx.prefix}{ctx.command}')

        await chn.send(embed=emb)
        
        data['idea'] +=1
        self.bot.write_json('data.json',data)

        emb = discord.Embed(description='[Ваша идея успешно отправлена](https://discord.gg/KXYkH5A)')
        emb.set_author(name=ctx.message.author.name, 
            icon_url= str(ctx.author.avatar_url))
        emb.set_footer(text=f'{ctx.prefix}{ctx.command}')

        await ctx.send(embed=emb)



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
            
            except:
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
    async def dashboard(self,ctx,id :int=None):
        """Просмотр информации про бота
        
        Пример: `f.dashboard 12` покажет запись с ID 12
        `f.dashboard` покажет последнюю запись"""

        dd = data['dashboard']

        if not id:
            val = dd[list(dd)[-1]]

            embed=discord.Embed(title=val['name'],description=val['value'],
                color=discord.Colour.light_grey())
            embed.set_footer(text=f'{ctx.prefix}{ctx.command}')

            await ctx.send(embed=embed)

        else:

            try:
                val = dd[str(id)]

                embed=discord.Embed(title=val['name'],description=val['value'],
                    color=discord.Colour.light_grey())
                embed.set_footer(text=f'{ctx.prefix}{ctx.command}')
                await ctx.send(embed=embed)

            except:
                await ctx.send('> :globe_with_meridians:  ID не найден')



    @commands.command(aliases=['dashboardAdd','dbAdd','addDb'],hidden=True)
    @commands.is_owner()
    async def addDashboard(self,ctx,*,content):
        """Добавить запись в Dashboard"""

        dc = await self.bot.read_json("config.json")
        dd = data['dashboard']

        id = str(int(list(dd)[-1]) + 1)

        dd[id] = {'name':f'ID: {id}, Author: {ctx.author.name}',"value":content}
        chn = await self.bot.fetch_channel(dc["dashboard channel"])
        emb = discord.Embed(description=f'Новая запись в Dashboard')
        emb.add_field(name=f'ID: {id}',value=content)
        emb.set_author(name=ctx.message.author.name, icon_url= str(ctx.author.avatar_url))
        emb.set_footer(text=f'{ctx.prefix}{ctx.command}')
        await chn.send(embed=emb)
        
        await self.bot.write_json('data.json',data)

        await ctx.send('> OK')



    @commands.command(aliases=['pdb'])
    async def publicDashboard(self,ctx,id :int=None):
        """Dashboard который заполнять могут все.
        Синтаксис идентичен комманде `dashboard`"""
        dd = data['pdb']
        if not id:
            val = dd[list(dd)[-1]]
            embed=discord.Embed(title=val['name'],description=val['value'],color=discord.Colour.light_grey())
            embed.set_footer(text=f'{ctx.prefix}{ctx.command}')
            await ctx.send(embed=embed)
        else:
            try:
                val = dd[str(id)]
                embed=discord.Embed(title=val['name'],description=val['value'],color=discord.Colour.light_grey())
                embed.set_footer(text=f'{ctx.prefix}{ctx.command}')
                await ctx.send(embed=embed)
            except:
                await ctx.send('> :globe_with_meridians:  ID не найден')
    
    
    
    @commands.command(aliases=['publicDashboardAdd','addPdb', 'addPublicDashboard'])
    @commands.cooldown(1, 300, commands.BucketType.member)
    async def pdbAdd(self,ctx,*,content):
        '''Позволяет добавить запись в Public Dashboard'''
        dc = await self.bot.read_json("config.json")
        dd = data['pdb']
        id = str(int(list(dd)[-1]) + 1)
        dd[id] = {'name':f'ID: {id}, Author: {ctx.author.name}',"value":content}
        chn = await self.bot.fetch_channel(dc["dashboard channel"])
        emb = discord.Embed(description=f'Новая запись в PDB')
        emb.add_field(name=f'ID: {id}',value=content)
        emb.set_author(name=ctx.message.author.name, icon_url= str(ctx.author.avatar_url))
        emb.set_footer(text=f'{ctx.prefix}{ctx.command}')
        await chn.send(embed=emb)
        await self.bot.write_json('data.json',data)

        await ctx.send('> OK')



def setup(bot):
    bot.add_cog(text_tools(bot))
