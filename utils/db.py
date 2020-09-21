import asyncpg
from typing import Union
from discord import User, Guild
from datetime import datetime

class SQL:
    """Requests to DB"""

    def __init__(self, pool: asyncpg.pool.Pool):
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
        result = await self.sql(f"SELECT * FROM {table}")
        return result

    async def rawGet(self, table: str, column: str, value):
        result = await self.sql(f"SELECT * FROM {table} WHERE {column}=$1", value)
        return result

    async def rawDelete(self, table: str, column: str, value):
        await self.sql(f"DELETE FROM {table} WHERE {column}={value}")

    async def rawWrite(self, table: str, *values):
        args_description = ''
        for i in range(1, len(values)+1):
            args_description += f'${i}, ' if i != len(values) else f'${i}'
        await self.sql(f"INSERT INTO {table} VALUES ({args_description});", *values)

    async def rawUpdate(self, table: str, primary_key: str, update_params: str, *values):
        args_description = ''
        for i in range(1, len(values)+1):
            args_description += f'${i}, ' if i != len(values) else f'${i}'
        await self.sql(f"INSERT INTO {table} VALUES ({args_description}) ON CONFLICT ({primary_key}) DO UPDATE SET {update_params};", *values)


class PrefixesSQL(SQL):
    """Requests to DB associated with prefixes"""

    def __init__(self, pool: asyncpg.pool.Pool, config: dict):
        super().__init__(pool)
        self.standartValue = config.get("prefix")

    async def get(self, obj: Union[User, Guild]) -> str:
        """Get user/guild's prefix from DB"""
        id = obj.id

        result = await self.rawGet(table="prefixes", column="id", value=id)

        prefix = result.get("value") if type(result) != list else self.standartValue
        # .get is dict function,
        # if value not recorded in table self.sql returns [], so we cannot use .get
        return prefix

    async def set(self, obj: Union[User, Guild], value: str):
        """(Re)sets user/guild prefix request to DB"""
        id = obj.id

        if value == self.standartValue:
            await self.rawDelete(table='prefixes', column='id', value=id)
            return 'Prefix reseted' # True
        await self.rawUpdate('prefixes', 'id', 'value=EXCLUDED.value', id, value) # table=prefixes, primary_key=id, update_params='value=EXCLUDED.value'

class IdeasSQL(SQL):
    """Requests to DB associated with bot ideas"""
    def __init__(self, pool: asyncpg.pool.Pool):
        super().__init__(pool)

    async def add(self, author: User, topic: str or None, description: str, timestamp: float = datetime.now().timestamp()):
        """Adds idea to DB."""
        await self.rawWrite('ideas', author.id, topic, description, timestamp)
        return len(await self.rawGetAll('ideas')) + 1

    