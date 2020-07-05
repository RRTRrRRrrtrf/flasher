# public-flasher

[Flasher Bot](https://discordapp.com/api/oauth2/authorize?client_id=677176212518600714&permissions=-1&scope=bot) code.
Flasher bot is Discord bot writed on [forked discord.py](https://github.com/Naomi-Bot-Open-Source/discord.py/)

# Requirments

### **Python 3.7+**
### PostgreSQL 10.12+

#### Pip modules:
* git+https://github.com/Naomi-Bot-Open-Source/discord.py/ (Install after jishaku!!!)
* git+https://github.com/Naomi-bot-open-source/naomi-paginator
* jishaku
  * psutil (optional)
* colormap
  * easydev
* googletrans
* youtube_dl (optional, for cogs.music)
* discord.py[voice] (optional, for cogs.music, jsk voice)
* asyncpg
* colorama

# Run

* Create PSQL database
  * Run commands in backup.psql (`\i /path/to/backup.psql`)
* Install required pip modules (`pip3 install -r requirments.txt`)
* Fill config.json
* Run using `python3 main.py`



###### Publishied with MIT license
