import asyncpg
from typing import Union
from discord import User, Guild
from datetime import datetime

class SQL:
    def __init__(self, pool: asyncpg.pool.Pool):
        """Requests to database.

        Arguments
        ---------
        pool: asyncpg.pool.Pool - Opened pool to DB
        """
        self.db = pool

    async def sql(self, code, *args):
        async with self.db.acquire() as connection:
            output = await connection.fetch(code, *args)
            await self.db.release(connection)
        # print(repr(output)) # For debug
        if len(output) == 1:
            return output[0]
        else:
            return output


    async def rawGetAll(self, table: str):
        """
        Gets all records from table.

        Arguments
        ---------
        table: str - Name of table
        """
        result = await self.sql(f"SELECT * FROM {table}")
        return result

    async def rawGet(self, table: str, column: str, value):
        """
        Gets records from database.

        Arguments
        ---------
        table: str - Name of table
        column: str - Column where will be check
        value - Value of column for check
        """
        result = await self.sql(f"SELECT * FROM {table} WHERE {column}=$1", value)
        return result

    async def rawDelete(self, table: str, column: str, value):
        """
        Deletes data from table.

        Arguments
        ---------
        table: str - Name of table
        column: str - Column where will be check
        value - Value of column for check
        """
        await self.sql(f"DELETE FROM {table} WHERE {column}={value}")

    async def rawWrite(self, table: str, *values):
        """
        Writes values.

        Arguments
        ---------
        table: str - Name of table
        *values - Values to record
        """
        args_description = ''
        for i in range(1, len(values)+1):
            args_description += f'${i}, ' if i != len(values) else f'${i}'
        await self.sql(f"INSERT INTO {table} VALUES ({args_description});", *values)

    async def rawUpdate(self, table: str, primary_key: str, update_params: str, returning: bool=False, *values):
        """
        Writes or updates values.

        Arguments
        ---------
        table: str - Name of table
        primary_key: str - Primary key, like 'id'
        update_params: str - Parameters for ON CONFLICT (primary_key) DO UPDATE SET ... Example - id=excluded.id
        returning: bool = False - Return recorded values?

        Returns
        ---------
        if returning==True
            asyncpg.Record of updated (created) row
        else
            Empty list
        """
        args_description = ''
    
        for i in range(1, len(values)+1): #  '$1, $2, $3'
            args_description += f'${i}, ' if i != len(values) else f'${i}'

        request = f"INSERT INTO {table} VALUES ({args_description}) ON CONFLICT ({primary_key}) DO UPDATE SET {update_params}" + (" RETURNING *" if returning else "")
        
        return await self.sql(request, *values)


class PrefixesSQL(SQL):
    def __init__(self, pool: asyncpg.pool.Pool, config: dict):
        """
        Requests to DB associated with prefixes.

        Arguments
        ---------
        pool: asyncpg.pool.Pool - Opened pool to DB
        config: dict - Bot config
        """
        super().__init__(pool)
        self.standartValue = config.get("prefix")

    async def get(self, obj: Union[User, Guild]) -> str:
        """
        Get user/guild's prefix from DB.

        Arguments
        ---------
        obj: discord.User or discord.Guild
        """
        _id = obj.id

        result = await self.rawGet(table="prefixes", column="id", value=_id)

        prefix = result.get("value") if not isinstance(result, list) else self.standartValue
        # .get is dict function,
        # if value not recorded in table self.sql returns [], so we cannot use .get
        return prefix

    async def set(self, obj: Union[User, Guild], value: str):
        """
        (Re)sets user/guild prefix.

        Arguments
        ---------
        obj: discord.User or discord.Guild
        value: str - new prefix
        """
        _id = obj.id

        if value == self.standartValue:
            await self.rawDelete(table='prefixes', column='id', value=_id)
            return 'Prefix reseted' # True
        await self.rawUpdate('prefixes', 'id', 'value=EXCLUDED.value', _id, value) # table=prefixes, primary_key=_id, update_params='value=EXCLUDED.value'

class IdeasSQL(SQL):
    def __init__(self, pool: asyncpg.pool.Pool):
        """
        Requests to database associated with ideas.

        Arguments
        ---------
        pool: asyncpg.pool.Pool - Opened pool to DB
        """
        super().__init__(pool)

    async def add(self, author: User, topic: str or None, description: str, timestamp: float = datetime.now().timestamp()):
        """
        Adds idea to DB.

        Arguments
        ---------
        author: discord.User - Author of idea
        topic: str or None - Idea topic
        descriptiom: str
        timestamp: float = datetime.now().timestamp() - UNIX timestamp
        """
        await self.rawWrite('ideas', author.id, topic, description, timestamp)
        return len(await self.rawGetAll('ideas')) + 1

class DashboardSQL(SQL):
    def __init__(self, pool: asyncpg.pool.Pool):
        """
        Requests to database associated with dashboard.

        Arguments
        ---------
        pool: asyncpg.pool.Pool - Opened pool to DB
        """
        super().__init__(pool)

    async def add(self, author: User, topic: str, description: str or None, timestamp: float = datetime.now().timestamp()):
        """
        Adds idea to DB.

        Arguments
        ---------
        author: discord.User - Author of idea
        topic: str or None - Idea topic
        descriptiom: str
        timestamp: float = datetime.now().timestamp() - UNIX timestamp
        """
        await self.rawWrite('dashboard', author.id, topic, description, timestamp)
        return len(await self.rawGetAll('dashboard')) + 1

    async def get(self):
        """Returns last 15 dashboard records."""
        return await self.sql("SELECT * from dashboard ORDER BY time DESC LIMIT 15;")
        
class EconomySQL(SQL):
    def __init__(self, pool: asyncpg.pool.Pool, bot_user: User):
        """
        Requests to database associated with economy.

        Arguments
        ---------
        pool: asyncpg.pool.Pool - Opened pool to DB
        bot_user: discord.User
        """
        super().__init__(pool)
        self.treasury = bot_user

    def _id(self, user: User):
        """Converts discord.User to int (id)."""
        if user == self.treasury:
            return self.treasury.id

        if user.bot:
            raise ValueError('Provided user - bot!')
        
        return user.id

    async def _get(self, _id: int):
        """Gets user's balance or inits it (set 0 value)."""
        result = await self.rawGet(table='eco', column='id', value=_id)

        if not result: # ID not recorded to DB, .sql function returns []
            await self.rawWrite('eco', _id, 0)
            return 0
        
        return float(result.get('coins'))

    async def get(self, user: User):
        """
        Gets user's balance
        
        Arguments
        ---------
        user: discord.User - User whose balance will be get. Provide bot user for treasury
        
        Returns
        ---------
        User balance (float)
        """
        _id = self._id(user)
        
        return await self._get(_id)

    async def set(self, user: User, amount: float):
        """
        Updates user balance
    
        Arguments
        ---------
        user: discord.User = None - User whose balance will be set. Provide bot user for treasury
        amount: float - New user balance
        """
        _id = self._id(user)

        await self.rawUpdate('eco', 'id', 'coins=excluded.coins', _id, amount) # table, primary key, update params, returning, *args

    async def add(self, user: User, amount: float):
        """
        Add coins to user balance
    
        Arguments
        ---------
        user: discord.User = None - User whose balance will be set. Provide bot user for treasury
        amount: float - Coins amount

        Returns
        ---------
        New user balance (float)
        """
        _id = self._id(user)
        new_balance = await self._get(_id) + amount

        await self.rawUpdate('eco','id','coins=excluded.coins', False, _id, new_balance) # table, primary key, update params, returning, *args
        return new_balance

    async def remove(self, user: User, amount: float=0):
        """
        Remove coins from user balance.
        For arguments and returned see EconomySQL.add
        """
        return await self.add(user, amount=-amount)