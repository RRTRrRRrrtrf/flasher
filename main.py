import discord # pylint: disable=import-error
from discord.ext import commands,tasks # pylint: disable=import-error
import asyncpg # pylint: disable=import-error

import time
import os
import traceback
import datetime
import json
import sys
import asyncio


from colorama import Fore, Back, init # pylint: disable=import-error

init(autoreset=True)
del init



def load_bot_config():
    try: 
        config = json.loads(open('config.json', 'r').read())
        print(Fore.GREEN + 'Config loaded')
        return config
    except:
        print(Back.RED + 'Error when config loading. Stopping')
        exit(1)


def load_flags_config():
        data = json.loads(open('flagConfig.json', 'r').read())
        keys = data.keys()
        for key in keys:
            os.environ[key] = data[key]
        print(Fore.GREEN + 'Flag config loaded')



SQL_REQUESTS = (
    '''
    CREATE TABLE IF NOT EXISTS dashboard (
        author bigint PRIMARY KEY CHECK (author > 0),
        topic varchar(60) NOT NULL,
        content varchar(512),
        time int NOT NULL
    );
    ''',

    '''
    CREATE TABLE IF NOT EXISTS ideas (
        author bigint PRIMARY KEY CHECK (author > 0),
        topic varchar(60),
        description varchar(512) NOT NULL,
        time int NOT NULL
    );
    ''',

    '''
    CREATE TABLE IF NOT EXISTS prefixes (
        id bigint PRIMARY KEY CHECK (id > 0),
        value varchar(7) NOT NULL
    );
    ''',

    '''
    CREATE TABLE IF NOT EXISTS eco (
        id bigint PRIMARY KEY CHECK (id > 0),
        coins decimal NOT NULL CHECK (coins >= 0)
    );
    ''',

    '''
    CREATE TABLE IF NOT EXISTS blacklist(
        id bigint PRIMARY KEY CHECK (id > 0)
    )
    '''
)

async def run():
    try:
        db = await asyncpg.create_pool(config["sqlPath"])        
        print(Fore.GREEN + 'Postgres connected')
    except:
        print(Back.RED + 'Postgres not loaded. Stoping')
        exit(1)

    for request in SQL_REQUESTS:
        await db.execute(request)   

    bot = Bot(db)
    await bot.start(config['token'], reconnect=True, bot=True)



class Bot(commands.Bot):
    def __init__(self, db):
        self.config = config
        self.db = db
        super().__init__(commands.when_mentioned_or(self.get_prefix), case_insensitive = True)

        self.load_extensions()
        self.started_at = datetime.datetime.now()
    

    
    
    
    async def sql(self, code, *args):
        async with self.db.acquire() as connection:
            output = await connection.fetch(code, *args)
            await self.db.release(connection)
        #print(repr(output)) # For debug
        if len(output) == 1:
            return output[0]
        else:
            return output




    async def get_prefix(self, msg):
        data = await self.sql(f'SELECT * FROM prefixes WHERE id={msg.author.id}')
        if not data: # <Record > case
            prefix = commands.when_mentioned_or(self.config["prefix"])
        else:
            prefix = commands.when_mentioned_or(data['value'])
            return prefix(self,msg)

        if msg.guild:
            data = await self.sql(f'SELECT * FROM prefixes WHERE id={msg.guild.id}')
            if not data: # <Record > case
                prefix = commands.when_mentioned_or(self.config["prefix"])
            else:
                prefix = commands.when_mentioned_or(data['value'])
        return prefix(self, msg)



    async def on_message(self, msg):
        if self.config["blacklistStatus"]:
            blacklisted = await self.sql(f'SELECT * FROM blacklist WHERE id = {msg.author.id};')
            if blacklisted: return 
        await self.process_commands(msg)



    async def on_message_edit(self,before,msg):
        await self.on_message(msg)	    # process commands by message edit



    async def on_ready(self):
        await self.change_presence(activity=discord.Game(
            f' {len(self.users)} пользователей | {self.config["prefix"]}help'))
        print(Back.BLUE + f'Bot online. Time is {time.ctime(time.time())}')
        


    def load_extensions(self):
        start = datetime.datetime.now()
        modules = self.config["extensions"]
        try: self.remove_command('help')
        except: pass
        for extension in modules:
            try:
                self.load_extension(extension)
                print( Fore.BLACK + Back.GREEN + f'{extension} loaded')
            except:
                print(Back.RED + 'Can\'t load {}:\n{}'.format(extension, traceback.format_exc()))
        end = datetime.datetime.now()
        t = end - start
        print(Back.BLUE + f'Load time: {t.microseconds/1000}ms')



    async def is_owner(self,member):
        owners = self.config["customOwnerList"]
        app = await self.application_info()

        if owners:
            return member.id in owners
        else:
            if app.team:
                return member.id in [x.id for x in app.team.members]
            else:
                return member.id == app.owner.id



    def restart(self):
        print(Back.BLUE + Fore.RED + '\n\n\nRestart\n\n')
        os.execl(sys.executable, sys.executable, *sys.argv)
        
        
        
    



if __name__ == "__main__":
    config = load_bot_config()
    load_flags_config()
    loop = asyncio.get_event_loop()
    try: 
        loop.run_until_complete(run())
    except KeyboardInterrupt:
        print(Fore.RED + '\nKeyboardInterrupt')