import discord # pylint: disable=import-error
from discord.ext import commands,tasks # pylint: disable=import-error
import time
import os
import traceback
import datetime
import json
import datetime
import sys
import asyncpg # pylint: disable=import-error
from colorama import Fore, Back, init 
init(autoreset=True)


class Flasher(commands.Bot):
    def __init__(self):
        self.config = self.load_bot_config()
        super().__init__(commands.when_mentioned_or(self.get_prefix), case_insensitive = True)
        self.load_flags_config()
        self.load_extensions()
        self.started_at = datetime.datetime.now()
    
    
    
    def load_bot_config(self):
        try:
            print(Fore.YELLOW + 'Config loading') 
            return json.loads(open('config.json', 'r').read())
        except:
            print(Back.RED + 'Error when config loading. Stopping')
            exit
        
        
    async def on_connect(self):
        try:
            self.db = await asyncpg.create_pool(self.config["sqlPath"])        
            print(Fore.GREEN + 'Postgres conntected')
        except:
            print(Back.RED + 'Postgres not loaded. Stoping')
            exit
    
    async def sql(self, code, *args, parse=False):
        outputs = []
        async with self.db.acquire() as conn:
            for line in code.split(';'):
                output = await conn.fetch(line, *args)
                outputs += output
            await self.db.release(conn)
        if not parse:
            return outputs
        else:
            return [dict(i) for i in outputs]



    async def get_prefix(self, msg):
        data = await self.sql(f'SELECT * FROM prefixes WHERE id={msg.author.id}', parse=True)
        if not data: # [] case
            prefix = commands.when_mentioned_or(self.config["prefix"])
        else:
            record = data[0]
            prefix = commands.when_mentioned_or(record['value'])
            return prefix(self,msg)

        if msg.guild:
            data = await self.sql(f'SELECT * FROM prefixes WHERE id={msg.guild.id}', parse=True)
            if not data: # [] case
                prefix = commands.when_mentioned_or(self.config["prefix"])
            else:
                record = data[0]
                prefix = commands.when_mentioned_or(record['value'])
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



    async def read_json(self, fn: str):
        with open(fn) as f:
            return json.load(f)



    def restart(self):
        print(Back.BLUE + Fore.RED + '\n\n\nRestart\n\n')
        os.execl(sys.executable, sys.executable, *sys.argv)
        
        
        
    def load_flags_config(self):
        data = json.loads(open('flagConfig.json', 'r').read())
        keys = data.keys()
        for key in keys:
            os.environ[key] = data[key]
        print(Fore.GREEN + 'Flag config loaded')



if __name__ == "__main__":
    data = json.loads(open('config.json', 'r').read())
    bot = Flasher()
    try:discord.gateway.IdentifyConfig.browser = 'Discord Android' # pylint: disable=no-member
    except AttributeError:pass
    bot.run(data['token'], reconnect=True, bot=True)
