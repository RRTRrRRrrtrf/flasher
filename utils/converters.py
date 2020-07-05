import requests
import io
from discord.ext import commands

class File(commands.Converter):
    async def convert(self, ctx, url = None):
        if ctx.attachments:
            url = ctx.attachment[0].url
        elif url:
            pass

        return io.BytesIO(requests.get(url).content)