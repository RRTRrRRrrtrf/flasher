import os
import json
import traceback

from colorama import Fore, Back, init  # pylint: disable=import-error

init(autoreset=True)
del init


def load_bot_config():
    try:
        config = json.loads(open("config.json", "r").read())
        print(Fore.GREEN + "Config loaded.")
        return config
    except Exception as e:
        print(Back.RED + f"Error {type(e).__name__} when config loading, stopping.") # type(e).__name__ returns exception class name
        exit(1)


def load_flags_config():
    try:
        data = json.loads(open("flagConfig.json", "r").read())
        keys = data.keys()
        for key in keys:
            os.environ[key] = data[key]
        print(Fore.GREEN + "Flags loaded.")
    except Exception as e:
        print(Back.RED + f"Error {type(e).__name__} when flags loading, passing.") # type(e).__name__ returns exception class name

def load_extensions(bot, extensions: tuple = None):
        """Loads extensions (cogs)"""

        modules = extensions or bot.config["extensions"]

        for extension in modules:
            
            try:
                bot.load_extension(extension)
                print(Fore.BLACK + Back.GREEN + f"An extension \"{extension}\" loaded")
            except:
                error = traceback.format_exc()
                print(Back.RED + f"An extension \"{extension}\" is not loaded.{Back.RESET} \n" + error)

SQL_REQUESTS = (
    """
    CREATE TABLE IF NOT EXISTS dashboard (
        author bigint CHECK (author > 0),
        topic varchar(60) NOT NULL,
        content varchar(512),
        time int NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS ideas (
        author bigint CHECK (author > 0),
        topic varchar(60),
        description varchar(512) NOT NULL,
        time int NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS prefixes (
        id bigint PRIMARY KEY CHECK (id > 0),
        value varchar(7) NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS eco (
        id bigint PRIMARY KEY CHECK (id > 0),
        coins decimal NOT NULL CHECK (coins >= 0)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS blacklist(
        id bigint PRIMARY KEY CHECK (id > 0)
    )
    """)
