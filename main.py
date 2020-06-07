import discord
from discord.ext import commands,tasks
import time
import os
import traceback
import datetime
import json
import datetime



class Flasher(commands.Bot):
    def __init__(self):
        super().__init__(commands.when_mentioned_or(self.get_prefix), case_insensitive = True)
        self.remove_command('help')
        self.prefix = 'f.'
        self.load()
        self.started_at = datetime.datetime.now()
        self.config = self.read_json('config.json')
        
        
    
    async def get_prefix(self, msg):
        prefixes = (await self.read_json('data.json'))["prefixes"]
        if str(msg.author.id) not in prefixes: 
            prefix = commands.when_mentioned_or('f.')
        else: 
            prefix = commands.when_mentioned_or(str(prefixes[str(msg.author.id)]))
        return prefix(self, msg)

    async def on_message(self, msg):
        if self.config["blacklistStatus"]:
            bl = (await self.read_json('blacklist.json'))
            if msg.author.id in bl["users"]: return
        await self.process_commands(msg)
	    
    async def on_ready(self):
        await self.change_presence(activity=discord.Game(f' {len(self.users)} пользователей | f.help'))
        print(f'Bot online. Time is {time.ctime(time.time())}')


    def load(self):
        start = datetime.datetime.now()
        modules = self.config["extensions"]
        for i in modules:
            try:
                self.load_extension(i)
                print(i, 'loaded')
            except:
                print('Can\'t load {}:\n{}'.format(i, traceback.format_exc()))
        end = datetime.datetime.now()
        t = end - start
        print(f'Load time: {t.microseconds/1000}ms')

    async def read_json(self, fn: str):
        with open(fn) as f:
            return json.load(f)
    async def write_json(self, fn: str, data):
        with open(fn, 'w') as f:
            json.dump(data, f)
    def read_json2(self, fn: str):
        with open(fn) as f:
            return json.load(f)
    def write_json2(self, fn: str, data):
        with open(fn, 'w') as f:
            json.dump(data, f)

    def restart(self):
        os.system("python3.7 main.py")
        exit()
        return f'Restarted succesfully. {time.ctime(time.time())}'



data = json.loads(open('config.json', 'r').read())





if __name__ == "__main__":
    bot = Flasher()
    discord.gateway.IdentifyConfig.browser = 'Discord Android'
    bot.run(data['token'], reconnect=True, bot=True)




