import discord
from discord.ext import commands, tasks

from random import uniform
from utils.db import EconomySQL # pylint: disable=all

class Economy(commands.Cog):
    def __init__(self, bot):
        """Команды экономики"""
        self.bot = bot
        self.anti_spam.start() # pylint: disable=no-member
        self.db = EconomySQL(self.bot.db, self.bot.user)

    ### Events and tasks

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context):

        if self.used_commands > 15:
            return
        self.used_commands += 1

        coins_to_add = self.bot.config.get("commandCost", 0.0166)
        await self.db.add(self.bot.user, coins_to_add)

    @tasks.loop(hours=6)
    async def anti_spam(self):
        self.used_commands = 0

    ### Commands

    
    @commands.command()
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def work(self, ctx):
        """Заработайте Flasher Coins"""
        min = self.bot.config["workPercentage"][0]
        max = self.bot.config["workPercentage"][1]
        percentage = uniform(min, max)

        
        treasury_coins = await self.db.get(self.bot.user)
        earnings = treasury_coins * percentage

        balance = await self.db.add(ctx.author, earnings)

        embed = discord.Embed(
            title=f"На баланс засчитано {round(earnings,6)} монет",
            description=f'Ваш баланс теперь составляет **`{round(balance, 6)}` монет**',
            color=discord.Colour.green())

        await ctx.send(embed=embed)

    @commands.command(aliases=["bal", "coins", "money"])
    async def balance(self, ctx, user: discord.Member = None):
        """Узнать ваш или чужой баланс"""

        if not user:
            user = ctx.author

        if user.bot:
            return await ctx.send("> Балансы для ботов предусмотрены не были, как и то что ботов будут обворовывать...")

        balance = await self.db.get(user)
        treasury = await self.db.get(self.bot.user)

        await ctx.send(
            f'> Баланс {user.name} **`{balance}`**\n'
            f'> Баланс казны **`{treasury}`**')

    @commands.command(aliases=["gift", "send"])
    async def pay(self, ctx, user: discord.Member, amount: float):
        """Отправить Flasher Coins кому либо"""
        if user == ctx.author:
            return await ctx.send('> Вы не можете отправить деньги самому себе!')
        if user.bot and user != self.bot.user:
            return await ctx.send('> Вы не можете отправить деньги боту!')
        
        amount = abs(amount)
        to_pay = amount * 1.15 # 15% tax
        has = await self.db.get(ctx.author)

        if amount > has:
            return await ctx.send('> Указанная сумма слишком большая для исполнения платежа!')
        if to_pay > has:
            reciever_balance = await self.db.add(user, amount) # Reciever
            await self.db.set(ctx.author, 0) # Sender
            return await ctx.send('Недостаточно денег для оплаты налога! Сумма переведена в полном размере, ваш баланс обнулён\n'
                f'> Списано *`{has}`*\n'
                f'> Переведено **`{amount}`**\n'
                f'> Баланс получателя `{reciever_balance}`')

        reciever_balance = await self.db.add(user, amount) # Reciever
        sender_balance = await self.db.remove(ctx.author, to_pay) # Sender
        return await ctx.send(f'> Списано *`{to_pay}`*\n'
            f'> Переведено **`{amount}`**\n'
            f'> Баланс получателя `{reciever_balance}`\n'
            f'> Баланс отправителя `{sender_balance}`')
            

def setup(bot):
    bot.add_cog(Economy(bot))
