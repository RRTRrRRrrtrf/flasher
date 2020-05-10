import discord
from discord.ext import commands
import time


class Message_Log(commands.Cog):

    def __init__(self,bot):
        self.bot = bot



    @commands.Cog.listener()
    @commands.guild_only()
    async def on_message(self,msg):

        if msg.guild.id in (489764714549739521,336642139381301249,624279965763895307) or msg.author.id is self.bot.user.id: return


        if msg.content or msg.attachments or msg.embeds:

            info = f'`{time.ctime(time.time())}` `{msg.guild.name} ({msg.guild.id})` `#{msg.channel.name} ({msg.channel.id})` {msg.author.name}#{msg.author.discriminator} ({msg.author.id}) : \n\n'

            if msg.attachments:
                for a in msg.attachments:
                    info += f'Attachment:{a.url}\n\n'
                    
            if msg.author.bot:
                info += 'Sent by bot.\n\n'

            if msg.embeds:
                emb = msg.embeds[0]
            else:
                emb=None

            ct = msg.content.replace('```','``')
            toSend = f'{info} ```{ct}```'
            if not msg.content: toSend = info
            
            dchannel = await self.bot.read_json('config.json')
            dchannel = await self.bot.fetch_channel(dchannel["debug channel"])

            try: await dchannel.send(toSend,embed=emb)
            except: await dchannel.send(info + 'An error when sending')


def setup(bot):
    bot.add_cog(Message_Log(bot))

