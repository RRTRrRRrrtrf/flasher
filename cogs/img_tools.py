import discord
from discord.ext import commands
from colormap import rgb2hex, rgb2hsv,hex2rgb
import aiohttp


class Image_tools(commands.Cog):

    def __init__(self,bot):
        self.bot = bot



    @commands.command(aliases=['rgb','color','colorEmbed','hex','hexEmbed'])
    async def rgbEmbed(self,ctx,red: int,green: int,blue: int):
        """Отправка эмбеды с цветом который вы указали
        
        :warning: Бот принимает только цветовую палитру RGB, показетели которой разделены пробелом а не запятой."""
        emb = discord.Embed(description=f'RGB:{red},{green},{blue}\nHEX:{rgb2hex(red,green,blue)}\nCMYK:В разаработке\nHSV:В разработке\nHSL:В разаработке',color=discord.Color.from_rgb(red,green,blue))
        emb.set_author(name=ctx.message.author.name, icon_url= str(ctx.author.avatar_url))
        emb.set_footer(text=f'{ctx.prefix}{ctx.command}' )
        await ctx.send(embed=emb)



    @commands.command(aliases=['ss'])
    @commands.cooldown(1, 8, commands.BucketType.member)
    @commands.is_nsfw()
    async def snapshot(self, ctx, *, url: str):
        ''' Сделать скриншот сайта
        
        ``/ss google.com``
        '''
# ChromeChain by Alice (developer of Naomi Bot), Command from artem6191
        if not ctx.channel.nsfw:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(embed=discord.Embed(title='Вы можете использовать эту комманду только в NSFW канале', color=discord.Colour.red()))
        msg = await ctx.send(embed=discord.Embed(title='Ожидаем ответ от API...'))
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://chromechain.herokuapp.com/?url={url}') as resp:
                    await msg.edit(content=None, embed=discord.Embed(color=ctx.author.color, title=url).set_image(url=(await resp.json())["content"]))
            await session.close()
        except:
            ctx.command.reset_cooldown(ctx)
            await msg.edit(content=None, embed=discord.Embed(title='Ошибка.', color=discord.Colour.red()))

    @commands.command(aliases=['mcskin','minecraftskin'])
    @commands.cooldown(1,5, commands.BucketType.member)
    async def skin(self,ctx,nickname: str):
        f"""Получить скин игрока. (Minecraft)
        
        Можно использовать как ник, так и UUID игрока.
        
        ``{ctx.prefix}skin TuxLabore``
        ``{ctx.prefix}skin e458d85f78af422f889226daaabf35ce``"""

        emb = discord.Embed(title=f'Скин игрока {nickname}', url=f'https://mc-heads.net/body/{nickname}/600')
        emb.set_image(url=f'https://mc-heads.net/body/{nickname}/600')
        emb.set_author(name=ctx.message.author.name, icon_url= str(ctx.author.avatar_url))
        emb.set_footer(text=f'{ctx.prefix}{ctx.command}' )
        await ctx.send(embed=emb)

    
def setup(bot):
    bot.add_cog(Image_tools(bot))