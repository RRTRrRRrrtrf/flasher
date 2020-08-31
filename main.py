import discord 
from discord.ext import commands, tasks  
import asyncpg  
from utils.db import PrefixesSQL, SQL

from Core.config import SQL_REQUESTS, load_bot_config, load_flags_config, load_extensions

from time import ctime
import os
import sys
import asyncio


from colorama import Fore, Back, init  

init(autoreset=True)
del init


async def run(): # Connects the database and starts bot.
    try:
        db = await asyncpg.create_pool(config["sqlPath"])
        print(Fore.GREEN + "PostgreSQL database connected.")
    except:
        print(Back.RED + "Database not connected, stoping.")
        exit(1)
    
    sql = SQL(db).sql

    for request in SQL_REQUESTS:
        await sql(request)

    bot = Bot(db)
    
    blacklisted = await sql("SELECT * FROM blacklist;")             # Gets blacklisted users list
    blacklisted = [record.get('id') for record in blacklisted] 
    
    del sql

    @bot.check                                                      
    def blacklist_check(ctx): # pylint: disable=unused-variable
        """Checks are user blacklisted"""
        if ctx.author.id not in blacklisted: 
            return True                                             # If not triggered True, bot check fails because returned None

    await bot.start(config["token"], reconnect=True, bot=True)


class Bot(commands.Bot):
    """Main class for bot"""
    def __init__(self, db):
        self.config = config
        
        self.db = db 
        self.sql = SQL(db).sql
        
        self.prefixes = PrefixesSQL(self.db, self.config)

        super().__init__(
            commands.when_mentioned_or(self.get_prefix), 
            case_insensitive=True, help_command=None) # help_command=None disables included in discord.py help command.
        
        load_extensions(self)


    async def on_message_edit(self, before, msg): # "before" is unused variable
        await self.process_commands(msg)  # process commands by message edit

    async def on_connect(self):
        print(Back.LIGHTBLUE_EX + f'Websocket connected on {ctime()}')

    async def on_ready(self):
        print(Back.BLUE + f"Bot ready on {ctime()}")
        
    async def get_prefix(self, msg):
        """Returns user/guild's prefix"""

        user_prefix = await self.prefixes.get(msg.author)

        if msg.guild:

            server_prefix = await self.prefixes.get(msg.guild)

            if user_prefix == self.config.get("prefix"):
                return server_prefix
            else:
                return user_prefix

        else:

            return user_prefix


if __name__ == "__main__":

    config = load_bot_config()
    load_flags_config()
    
    loop = asyncio.get_event_loop()
    
    try:
        loop.run_until_complete(run())
    except KeyboardInterrupt:
        print(Fore.RED + "\nKeyboardInterrupt")
