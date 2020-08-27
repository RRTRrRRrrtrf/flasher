import os
import json

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