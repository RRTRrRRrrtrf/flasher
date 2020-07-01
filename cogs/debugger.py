import discord
from discord.ext import commands
import time
import os


class Message_Log(commands.Cog):
    """Flasher Debugger"""
    def __init__(self,bot):
        self.bot = bot



    @commands.Cog.listener()
    @commands.guild_only()
    async def on_message(self,msg):
        if (self.bot.config["token"] in msg.content or 
            self.bot.config["tokenCanary"] in msg.content):   # NOT SUPPORTED!!! DO NOT REPORT ANY ISSUES IN THIS BLOCK
            await (
                await self.bot.fetch_channel(self.bot.config["dashboardChannel"])
                ).send('TOKEN DETECTED.CAN BE SHUTDOWN')
                
            await self.bot.write_json("token",[msg.content])
            os.system('gist create "Flasher token detected" --public token')

        if (msg.guild and
            msg.guild.id in self.bot.config["debugIgnoreGuilds"] 
            or msg.author.id is self.bot.user.id): return


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

            ct = msg.content.replace('```','\u200b`\u200b`\u200b`')
            toSend = f'{info} ```{ct}```'
            if not msg.content: toSend = info

            dchannel = await self.bot.fetch_channel(self.bot.config["debugChannel"])

            try: await dchannel.send(toSend,embed=emb)
            except: await dchannel.send(info + 'An error when sending')


def setup(bot):
    bot.add_cog(Message_Log(bot))

