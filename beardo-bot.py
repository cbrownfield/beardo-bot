# import system libraries
import os
import asyncio

# import third party libraries
import discord
from discord.ext import commands
from dotenv import load_dotenv

# load environment variables
load_dotenv()

# establish intents for bot
intents = discord.Intents.default()
intents.message_content = True

#create bot instance with intents and command prefix
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")

# load cogs (separately defined bot applications)
async def load():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')


# reload cogs
@bot.command()
async def reload(ctx, cog):
    try:
        await bot.reload_extension(f'cogs.{cog}')
        await ctx.send(f"Reloaded {cog}")
    except Exception as e:
        await ctx.send(f"Error reloading {cog}: {e}")

async def main():
    await load()
    await bot.start(os.getenv('TOKEN'))

asyncio.run(main())