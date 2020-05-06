import discord
import asyncio
from random import choice

class Entry:
    def __init__(self, name, value, image=None):
        self.name = name
        self.value = value
        self.image = image


class Paginator:
    def __init__(self, ctx, bot, title):
        self.ctx = ctx
        self.bot = bot
        self.title = title
        self.pages = []
        self.active  = True
        self.emojis = '<:fastback:662329240695603231> <:back:662329241261703168> <:stop:662329241601310749> <:forward:662329240565579787> <:fastforward:662329241022496778>'.split(' ')

    async def paginate(self):
        try:
            self.page_c = 0
            page_c = self.page_c
            page = self.pages[page_c]
            embed = discord.Embed(description=page.name)
            embed.set_footer(text=f'{page.value[0]} • ' + 'Страница {}/{}'.format(self.page_c + 1, len(self.pages)), icon_url=page.value[1])
            if page.image == None: pass
            else: embed.set_image(url=page.image)

            self.message = await self.ctx.send(embed=embed)

            message = self.message
            for reaction in self.emojis: await message.add_reaction(str(reaction))
            
            async def loop1():
                while self.active == True:
                    try:
                        r, u = await self.bot.wait_for('reaction_add', check=lambda r,u: u.id == self.ctx.author.id and r.message.id == message.id, timeout=120)
                    except asyncio.TimeoutError:
                        try: await self.message.clear_reactions()
                        finally: self.active = False  
                    else:   
                        if str(r) == '<:forward:662329240565579787>':
                            p = self.page_c + 1 
                            await self.to_page(p)
                        elif str(r) == '<:back:662329241261703168>':
                            p = self.page_c - 1
                            await self.to_page(p)

                        elif str(r) == '<:fastforward:662329241022496778>':
                            p = len(self.pages)-1
                            await self.to_page(p)
                        elif str(r) == '<:fastback:662329240695603231>':
                            p = 0
                            await self.to_page(p)
                        elif str(r) == '<:stop:662329241601310749>':
                            self.active = False
                            await self.message.delete()
            async def loop2():
                while self.active == True:
                    try:
                        r, u = await self.bot.wait_for('reaction_remove', check=lambda r,u: u.id == self.ctx.author.id and r.message.id == message.id, timeout=120)
                    except asyncio.TimeoutError:
                        try: await self.message.clear_reactions()
                        finally: self.active = False  
                    else:   
                        if str(r) == '<:forward:662329240565579787>':
                            p = self.page_c + 1 
                            await self.to_page(p)
                        elif str(r) == '<:back:662329241261703168>':
                            p = self.page_c - 1
                            await self.to_page(p)

                        elif str(r) == '<:fastforward:662329241022496778>':
                            p = len(self.pages)-1
                            await self.to_page(p)
                        elif str(r) == '<:fastback:662329240695603231>':
                            p = 0
                            await self.to_page(p)
                        elif str(r) == '<:stop:662329241601310749>':
                            self.active = False
                            await self.message.delete()
            self.task1 = self.bot.loop.create_task(loop1())
            self.task2 = self.bot.loop.create_task(loop2())
        except Exception as e:
            print(type(e).__name__, e)
            self.active = False
            return
                
                        
    def add_page(self, page: Entry):
        self.pages.append(page)


    async def to_page(self, page):
        if page == len(self.pages): page = 0
        elif page < 0: page = len(self.pages)-1
        self.page_c = page
        page = self.pages[self.page_c]
        embed = discord.Embed(description=page.name)
        embed.set_footer(text=f'{page.value[0]} • ' + 'Страница {}/{}'.format(self.page_c + 1, len(self.pages)), icon_url=page.value[1])

        await self.message.edit(embed=embed, content=None)