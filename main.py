import time
import discord
from discord.ext import commands
import discord
from os import listdir, environ
from dotenv import load_dotenv
from DatabaseCon import DatabaseCon
from PointsManagement import PointsManagement
from SkillManagement import SkillManagement
from Roles import RoleManagement


cogs_path = "./cogs"
load_dotenv("./.env")
token = environ.get("BOT_TOKEN")
guild_id = environ.get("GUILD_ID")


def get_prefix(bot, message):

    prefixes = ['.']

    if not message.guild:
        return '?'

    return commands.when_mentioned_or(*prefixes)(bot, message)


intents = discord.Intents().all()

bot: commands.Bot = commands.Bot(
    command_prefix=get_prefix, description='Points bot', intents=intents,
    activity=discord.Activity(
    ))


if __name__ == '__main__':
    for cog in listdir('./cogs'):
        if cog.endswith('.py') == True and "Utils" not in cog:
            print(f"Loading {cog}")
            bot.load_extension(f'cogs.{cog[:-3]}')


@bot.event
async def on_ready():
    if bot is not None:
        print(
            f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')
        print(f'Successfully logged in and booted...!')
        # Displays 'Watching 3 users'
        await bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.playing,
            name="DM Gabulhas#7229 for custom bots"

        ))

        bot.points_management = PointsManagement()
        bot.role_management = RoleManagement()
        bot.skill_management = SkillManagement()
        bot_guild: discord.Guild = bot.get_guild(int(guild_id))
        bot.role_management.load_roles(await bot_guild.fetch_roles())

bot.run(token, reconnect=True)
