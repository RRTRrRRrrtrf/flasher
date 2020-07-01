import discord
from discord.ext import commands,tasks
import time
import os
import traceback
import datetime
import json
import datetime
import sys
import asyncpg



class Flasher(commands.Bot):
    def __init__(self):
        super().__init__(commands.when_mentioned_or(self.get_prefix), case_insensitive = True)
        self.config = json.loads(open('config.json', 'r').read())
        self.load()
        self.started_at = datetime.datetime.now()
        
        
        
    async def get_prefix(self, msg):
        if not msg.guild:
            prefix = commands.when_mentioned_or(self.config["prefix"])
            return prefix(self, msg)
        data = await self.sql(f'SELECT * FROM prefixes WHERE id={msg.guild.id}', parse=True)
        if not data: # [] case
            prefix = commands.when_mentioned_or(self.config["prefix"])
        else:
            record = data[0]
            prefix = commands.when_mentioned_or(record['value'])
        return prefix(self, msg)



    async def on_message(self, msg):
        if self.config["blacklistStatus"]:
            bl = (await self.read_json('blacklist.json'))
            if msg.author.id in bl["users"]: return
        await self.process_commands(msg)

    async def on_message_edit(self,before,msg):
        if not msg.author.guild_permissions.send_messages: return
        if self.config["blacklistStatus"]:
            bl = (await self.read_json('blacklist.json'))
            if msg.author.id in bl["users"]: return
        await self.process_commands(msg)    
	    


    async def on_ready(self):
        await self.change_presence(activity=discord.Game(
            f' {len(self.users)} пользователей | {self.config["prefix"]}help'))
        print(f'Bot online. Time is {time.ctime(time.time())}')
        
    async def on_connect(self):
        self.db = await asyncpg.create_pool(self.config["sqlPath"])

    def load(self):
        start = datetime.datetime.now()
        modules = self.config["extensions"]
        try: self.remove_command('help')
        except: pass
        for i in modules:
            try:
                self.load_extension(i)
                print(i, 'loaded')
            except:
                print('Can\'t load {}:\n{}'.format(i, traceback.format_exc()))
        end = datetime.datetime.now()
        t = end - start
        print(f'Load time: {t.microseconds/1000}ms')



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



    async def write_json(self, fn: str, data):
        with open(fn, 'w') as f:
            json.dump(data, f)



    def restart(self):
        os.system(self.config["pythonCommand"] + " main.py")
        sys.exit()
        return f'Restarted succesfully. {time.ctime(time.time())}'
    


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


    def reload_config(self):
        self.config = json.loads(open('config.json', 'r').read())



data = json.loads(open('config.json', 'r').read())





if __name__ == "__main__":
    bot = Flasher()
    discord.gateway.IdentifyConfig.browser = 'Discord Android'
    bot.run(data['token'], reconnect=True, bot=True)




