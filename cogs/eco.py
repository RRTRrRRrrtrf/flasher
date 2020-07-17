import discord
from discord.ext import commands, tasks
from time import time
from random import randint
from typing import Union

class Economy(commands.Cog):
    """Команды экономики"""

    def __init__(self, bot):
        self.used_commands = 0
        self.bot = bot
        self.Treasury_id = 10000000000000000 # If changed do INSERT INTO eco VALUES (new_id_here,0)
        self.anti_spam.start()


    async def initUser(self, user: discord.User , sqlResult):
        if not sqlResult: # [] case
            await self.bot.sql('INSERT INTO eco VALUES ($1, 0)', user.id)
            return 0
        else:
            return float(sqlResult['coins'])


    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context):
        
        if self.used_commands > 200: return
        self.used_commands += 1

        coins_to_add = 1 / 60 
        status_now = await self.bot.sql("SELECT * FROM eco WHERE id=$1;", self.Treasury_id)
        
        coins_to_add += float(status_now['coins'])
        await self.bot.sql("UPDATE eco SET coins=$2 WHERE id=$1;", self.Treasury_id, coins_to_add)



    @tasks.loop(hours=6)
    async def anti_spam(self):
        self.used_commands = 0

    @commands.command()
    @commands.cooldown(1,3600, commands.BucketType.user)
    async def work(self,ctx):
        """Заработайте Flasher Coins"""
        cnfg = self.bot.config
        percentage = randint(cnfg['workPercentage'][0],cnfg['workPercentage'][1])/cnfg['workPercentage'][2] # Standart: 1-8 /100 -> 1-8% 
        tax_percentage = randint(cnfg['taxPercentage'][0],cnfg['taxPercentage'][1])/cnfg['taxPercentage'][2] 
        
        treasury_coins = await self.bot.sql(
            "SELECT * FROM eco WHERE id=$1;", self.Treasury_id)
        treasury_coins = float(treasury_coins['coins'])
        
        has = (await self.bot.sql(
            "SELECT * FROM eco WHERE id=$1;", ctx.author.id))
        has = await self.initUser(ctx.author, has)
        
        full = treasury_coins * percentage
        deFacto = full - full*tax_percentage
        
        await self.bot.sql("UPDATE eco SET coins=$1 WHERE id=$2", 
                           treasury_coins - deFacto, self.Treasury_id)
        await self.bot.sql("UPDATE eco SET coins=$1 WHERE id=$2", 
                           has+deFacto, ctx.author.id)
        
        embed = discord.Embed(title='На баланс засчитано %s FlC' % round(deFacto, 6),
                              description=f"""Зароботок: {round(full, 6)},
                              Налоговый сбор {round(full-deFacto, 6)},
                              Состояние баланса {round(deFacto+has, 6)}.""",
                              color=discord.Colour.green())
        
        await ctx.send(embed=embed)



    @commands.command(aliases=['bal','coins','money'])
    async def balance(self,ctx,user: discord.User = None):
        """Узнать ваш или чужой баланс"""
        
        if not user: user = ctx.author
        
        if user.bot:
            return await ctx.send('> Балансы для ботов предусмотрены не были, как и то что ботов будут обворовывать...')
        і
        has = await self.bot.sql("SELECT * FROM eco WHERE id=$1;", user.id)
        treasury_coins = float((await self.bot.sql("SELECT * FROM eco WHERE id=$1;", self.Treasury_id))['coins'])
        all_coins = sum( ( float(x['coins']) for x in await self.bot.sql('SELECT coins FROM eco') ) )
        
        has = await self.initUser(user, has)
        
        await ctx.send(f"> Баланс {user.name} - **`{round(has,6)}`**\n"
                       f"> Баланс казны - `{round(treasury_coins,6)}`\n"
                       f"> Существует Flasher Coins - `{round(all_coins,6)}`\n"
                       f"> Все Flasher Coins (кроме казны) - `{round(all_coins - treasury_coins, 6)}`")
        
        
    @commands.command(aliases=['gift','send'])
    async def pay(self,ctx,user: Union[discord.User, str], amount: float):
        """Отправить Flasher Coins кому либо"""
        topay = amount * 1.15 # 15% tax
        
        if type(user) is str:
            list = ['kazna','казна','treasury','tax','work','налог']
            if user not in list:
                return await ctx.send('> Укажите правильного пользователя или "Казна" для оплаты в казну :no_entry:')
            else:
                id = self.Treasury_id
                topay = amount
        else:
            id = user.id
            
        has = await self.bot.sql("SELECT * FROM eco WHERE id=$1;", ctx.author.id)
        has = await self.initUser(ctx.author, has)
        
        if topay > has:
            return await ctx.send('Недостаточно монет для проведения платежа :no_entry:\n'
                    f'> **Вам необходимо ещё** `{topay - has}` монет\n'
                    f'> Налоговый сбор составляет {str(topay-amount)[:6]}' )
        if amount < 0 and user.bot: # easter egg
            return await ctx.send('Ну это уже верх наглости, воровать, так ещё и у бота! Я вызываю полицию.')
        if user.id == ctx.author.id:
            return await ctx.send('> Оплата в казну происходит непосредсвенно через указание '
                'в поле "пользователь" слова казна, не надо платить себе что бы внести туда платёж :no_entry:')
        if user.bot:
            return await ctx.send('> Боту не нужны ваши деньги :no_entry:')
        if amount < 0:
            return await ctx.send('> Не пытайтесь украсть чужие деньги :no_entry:')
            
        hasReciever = await self.bot.sql("SELECT * FROM eco WHERE id=$1;", id)
        hasReciever = await self.initUser(user, hasReciever)
        
        await self.bot.sql("UPDATE eco SET coins=$2 WHERE id=$1", ctx.author.id, has-topay)
        await self.bot.sql("INSERT INTO eco (id,coins) VALUES ($1, $2) "
                            "ON CONFLICT (id) DO UPDATE SET coins=EXCLUDED.coins;", id, hasReciever + amount)
        
        await ctx.send('> OK')



def setup(bot):
    bot.add_cog(Economy(bot))
