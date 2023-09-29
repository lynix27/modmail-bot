import discord
from discord.ext import commands
import os
import aiohttp
from dotenv import load_dotenv
import logging
from discord.app_commands import AppCommandError
import aiomysql
from discord import app_commands

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

class MyBot(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix = commands.when_mentioned,
            intents = discord.Intents.default(),
            status=discord.Status.online,
            activity=discord.Game(name="with your tickets ✉️"))

    async def setup_hook(self):
        conn = await aiomysql.connect(
            host=os.getenv("HOST"),
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD"),
            db=os.getenv("DB"),
            autocommit=True
        )
        cursor = await conn.cursor()
        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS setup_category (
                SERVERID VARCHAR(100) PRIMARY KEY,
                CATEGORYID VARCHAR(100)
            )
            """
        )
        print("✅ Created setup_category database")

        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS log_channels (
                SERVERID VARCHAR(100) PRIMARY KEY,
                CHANNELID VARCHAR(100)
            )
            """
        )
        print("✅ Created log_channels database")

        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ticket_channels (
                SERVERID VARCHAR(100) PRIMARY KEY,
                CHANNELID VARCHAR(100)
            )
            """
        )
        print("✅ Created ticket_channels database")

        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ticket_messages (
                SERVERID VARCHAR(100) PRIMARY KEY,
                CHANNELID VARCHAR(100),
                MESSAGEID VARCHAR(100)
            )
            """
        )
        print("✅ Created ticket_messages database")

        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ticket_categories (
                SERVERID VARCHAR(100) PRIMARY KEY,
                CATEGORYID VARCHAR(100)
            )
            """
        )
        print("✅ Created ticket_categories database")

        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ticket_button_messages (
                SERVERID VARCHAR(100) PRIMARY KEY,
                MESSAGE TEXT
            )
            """
        )
        print("✅ Created ticket_button_messages database")

        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ticket_manager_roles (
                SERVERID VARCHAR(100) PRIMARY KEY,
                ROLEID VARCHAR(100),
                STATE TEXT
            )
            """
        )
        print("✅ Created ticket_manager_roles database")

        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS languages (
                SERVERID VARCHAR(100) PRIMARY KEY,
                LANGUAGE TEXT
            )
            """
        )
        print("✅ Created languages database")

        await cursor.close()
        conn.close()

        self.session = aiohttp.ClientSession()
        for f in os.listdir("./cogs"):
            if f.endswith(".py"):
                await self.load_extension("cogs." + f[:-3])
        await self.load_extension('jishaku')
        print("Loaded all extensions.")
        await bot.tree.sync()

    async def on_ready(self):
        print(f'{self.user} is now online. [{self.user.id}]')

            
bot = MyBot()

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: AppCommandError):
    await interaction.response.send_message(error, ephemeral=True)

@bot.event
async def on_command_error(ctx: commands.Context, error: discord.errors):
    await ctx.reply(error)

@bot.tree.command(name="set-language")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.choices(
    language = [
        app_commands.Choice(name="English", value="en"),
        app_commands.Choice(name="German", value="de"),
        app_commands.Choice(name="Spanish", value="es")
    ]
)
async def set_language(interaction: discord.Interaction, language: app_commands.Choice[str]):
    await interaction.response.defer(ephemeral=True)
    conn = await aiomysql.connect(
        host=os.getenv("HOST"),
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        db=os.getenv("DB"),
        autocommit=True
    )
    cursor = await conn.cursor()
    if language.value == "en":
        await cursor.execute("INSERT INTO languages (SERVERID, LANGUAGE) VALUES (%s, %s) ON DUPLICATE KEY UPDATE LANGUAGE = %s", (interaction.guild.id, language.value, language.value,))

    if language.value == "de":
        await cursor.execute("INSERT INTO languages (SERVERID, LANGUAGE) VALUES (%s, %s) ON DUPLICATE KEY UPDATE LANGUAGE = %s", (interaction.guild.id, language.value, language.value,))

    if language.value == "es":
        await cursor.execute("INSERT INTO languages (SERVERID, LANGUAGE) VALUES (%s, %s) ON DUPLICATE KEY UPDATE LANGUAGE = %s", (interaction.guild.id, language.value, language.value,))

    await cursor.close()
    conn.close()
    await interaction.followup.send(f"Language set to **{language.name}**", ephemeral=True)

load_dotenv()
bot.run(os.getenv("TOKEN"))