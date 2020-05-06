import discord
from discord.ext import commands
import time
import random
from colormap import rgb2hex, rgb2hsv,hex2rgb
import aiohttp


class img_tools(commands.Cog):

    def __init__(self,bot):
        self.bot = bot



    @commands.command(aliases=['rgb','color','colorEmbed','hex','hexEmbed'])
    async def rgbEmbed(self,ctx,red: int,green: int,blue: int):




        #if red and green and blue:
        emb = discord.Embed(description=f'RGB:{red},{green},{blue}\nHEX:{rgb2hex(red,green,blue)}\nCMYK:В разаработке\nHSV:В разработке\nHSL:В разаработке',color=discord.Color.from_rgb(red,green,blue))
        emb.set_author(name=ctx.message.author.name, icon_url= str(ctx.author.avatar_url))
        emb.set_footer(text='/color' )
        await ctx.send(embed=emb)
        '''elif red.startswith('#'):
            emb = discord.Embed(description=f'RGB:{hex2rgb(red)}\nHEX:{red}\nCMYK:В разаработке\nHSV:В разработке\nHSL:В разаработке',color=discord.Color.from_rgb(hex2rgb(red)))
            emb.set_author(name=ctx.message.author.name, icon_url= str(ctx.author.avatar_url))
            emb.set_footer(text='/color' )
            await ctx.send(embed=emb)
        else:
            emb = discord.Embed(description=f'Используйте RGB или HEX',color=discord.Colour.red)
            emb.set_author(name=ctx.message.author.name, icon_url= str(ctx.author.avatar_url))
            emb.set_footer(text='/color' )
            await ctx.send(embed=emb)    
        '''

    @commands.command(aliases=['ss'])
    @commands.cooldown(1, 8, commands.BucketType.member)
    @commands.is_nsfw()
    async def snapshot(self, ctx, *, url: str):
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

    @commands.command(aliases=['lengst','length'])                                                            # Пример для вас = 14
    async def len(self,ctx,*,textArg=None):
        '''Обчислить длину строки

        Пример: `/len abcd` -> `4`
        '''
        if textArg != None:
            textFixed = textArg.replace('``',"`\`")                             # Это необходимо для того что бы `` не ломало блок кода в эмбеде
            embed=discord.Embed(description=f'Длина вашей строки ``{textFixed}`` - {len(textArg)}')
            embed.set_author(name=ctx.message.author.name, icon_url= str(ctx.author.avatar_url))
            embed.set_footer(text='/len')
            await ctx.send(embed=embed)
            
        else:
            embed=discord.Embed(description=f'Ошибка: вы не указали текст для обработки',color= discord.Color.red)
            embed.set_author(name=ctx.message.author.name, icon_url= str(ctx.author.avatar_url))
            embed.set_footer(text='/lengst' )
            await ctx.send(embed=embed)



    
def setup(bot):
    bot.add_cog(img_tools(bot))