import discord
from discord.ext import commands
import time


class Message_Log(commands.Cog):

    def __init__(self,bot):
        self.bot = bot



    @commands.Cog.listener()
    @commands.guild_only()
    async def on_message(self,ctx):

        bl = await self.bot.read_json('blacklist.json')
        if ctx.guild.id in bl["log"]: return

        #banned = ('<@!','<@&','@here','@everyone')
        bi = await self.bot.read_json('config.json')
        bi = bi["bot id"]   

        if ctx.author.id != bi and ctx.content or ctx.attachments:

            info = f'`{time.ctime(time.time())}` `{ctx.guild.name} ({ctx.guild.id})` `#{ctx.channel.name} ({ctx.channel.id})` {ctx.author.name}#{ctx.author.discriminator} ({ctx.author.id}) : \n\n'

            if ctx.attachments:
                for a in ctx.attachments:
                    info += f'Attachment:{a.url}\n\n'
                    
            if ctx.author.bot:
                info += 'Sent by bot.\n\n'
            ct = ctx.content.replace('```','``')
            toSend = f'{info} ```{ct}```'
            if not ctx.content: toSend = info
            
            dchannel = await self.bot.read_json('config.json')
            dchannel = await self.bot.fetch_channel(dchannel["debug channel"])

            #for i in banned:
            #    toSend = toSend.replace(i,'**`PING DELETED`**')

            try: await dchannel.send(toSend)
            except: await dchannel.send(info + 'An error when sending')

    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def logBlacklist(self,ctx):
        '''Используйте на своем сервере что бы бот не записывал сообщения'''

        bl = await self.bot.read_json('blacklist.json')
        if ctx.guild.id in bl["log"]: await ctx.send('> Уже в списке игнорирования'); return     

        bl["log"].append(ctx.guild.id)
        await self.bot.write_json('blacklist.json',bl)
        await ctx.send('> OK')

    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def logPardon(self,ctx):
        '''Используйте на своем сервере если вы хотите что бы бот снова записывал сообщения'''
        
   
        
        bl = await self.bot.read_json('blacklist.json')
        bl["log"].remove(ctx.guild.id)
        await self.bot.write_json('blacklist.json',bl)
        await ctx.send('> OK')


def setup(bot):
    bot.add_cog(Message_Log(bot))

