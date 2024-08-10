from discord.ext import commands, tasks
import bs4
import requests
import datetime


class ArmaServerStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tree = bot.tree
        self.server_status.start()
        self.counter = 0

    # chat command to stop the server status loop, mainly for debugging
    @commands.command(name="status_break")
    async def server_status_stop(self, ctx):
        self.server_status.stop()
        await ctx.send("Server status loop stopped via command.")

    # chat command to start the server status loop, mainly for debugging
    @commands.command(name="start")
    async def server_status_start(self, ctx):
        print("Server status loop started via command.")
        self.server_status.start()

    # pull server status from battlemetrics and update the server status channel, runs every 2 minutes
    @tasks.loop(seconds=120)
    async def server_status(self):
        # get the server status channel
        statusChannel = self.bot.get_channel(1271809993292648511)
        print("checking server status...")
        
        #scrape the battlemetrics page for the S&S server
        page = requests.get("https://www.battlemetrics.com/servers/reforger/28190618")
        page.raise_for_status()

        # parse the page
        serverSoup = bs4.BeautifulSoup(page.text, 'lxml')
        
        # select the CSS selector with the server stats
        serverStats = serverSoup.select(".dl-horizontal")

        # pull the player count, server IP, and server status into varibles by string slicing
        playerCount = (serverStats[0].getText()[20:24]).split("/")
        playerCountFormatted = playerCount[0] + "/" + playerCount[1]
        #serverIp = (serverStats[0].getText()[32:51])
        serverStatus = (serverStats[0].getText()[57:63]).title()
        print("parsing server info...")
        
        # checks for previous messages in the channel to determine if a new message should be sent or an existing message should be edited
        channelHistory = [message async for message in statusChannel.history(limit=5)]
        print("checking channel history...")
        if not channelHistory:
            print("channel history is empty...")
            if serverStatus == "offline": 
                await statusChannel.send(content=f"Server is {serverStatus} with {playerCountFormatted} players.")
                await statusChannel.edit(name="\U0001F534" + "Server")
            else:
                await statusChannel.send(content=f"Server is {serverStatus} with {playerCountFormatted} players.")
                await statusChannel.edit(name="\U0001F7E2" + "Server")
        else:
            print("channel history is not empty...")
            armaStatusMessage = await statusChannel.fetch_message(statusChannel.last_message_id)
            if serverStatus == "offline": 
                await armaStatusMessage.edit(content=f"Server is {serverStatus} with {playerCountFormatted} players.")
                await statusChannel.edit(name="\U0001F534" + "Server")
            else:
                await armaStatusMessage.edit(content=f"Server is {serverStatus} with {playerCountFormatted} players.")
                await statusChannel.edit(name="\U0001F7E2" + "Server")
    
    # wait for the bot to be ready before starting the server status loop
    @server_status.before_loop
    async def before_server_status(self):
        print("waiting...")
        await self.bot.wait_until_ready()
        print("ready...")

    # purge the server status channel of messages every 24 hours
    @tasks.loop(time=datetime.time(hour=0, minute=0, tzinfo=datetime.timezone.utc))
    async def purge(self):
        statusChannel = self.bot.get_channel(1271809993292648511)
        await statusChannel.purge(limit=100)

async def setup(bot):
    await bot.add_cog(ArmaServerStatus(bot))