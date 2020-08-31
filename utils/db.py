import asyncpg
from typing import Union
from discord import User, Guild


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

    async def rawGet(self, table: str, column: str, value):
        result = await self.sql(f"SELECT * FROM {table} WHERE {column}={value}")
        return result


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
