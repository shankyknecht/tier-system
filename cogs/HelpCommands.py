import asyncio
from datetime import datetime
from typing import List, Tuple
import discord
from discord.ext import commands
from discord import Embed
from dotenv.main import load_dotenv
from os import environ
from random import randint
import time
import traceback

# This is trashy
commands_help = [
    ("help", "Shows this list. Use the \"staff\" argument to display staff commands"),
    ("p/points", "Shows oneself's points"),
    ("highscores", "Displays top 10 of points"),
    ("ranks", "Shows all ranks and it's minimum points to earn it"),
    ("[skill] [Optional:start-end levels]",
     "Calculates or shows all the methods for a specific skill. Examples: \n.rc 90-99 \n.woodcutting 80-99"),
]

staff_commands_help = [
    ("reset_all", "Resets all user points and roles."),
    ("add User Ammount", "Adds points to User."),
    ("remove User Ammount", "Takes points from User."),
    ("update User Ammount", "Updates/Sets User points to Ammount."),
    ("reset User", "Resets User points."),
    ("pcheck/points_check User", "Displays User points."),
    ("sp/staff_points [Optional: Staff]",
     "Displays all Staff Members' points, or single Staff Member's points."),
    ("add_calc [skill] [start]-[finish] [amount]gp/xp [method_name]",
     "Adds range to the calculator"),
    ("list_methods [skill]", "Lists all the methods for a skill"),
    ("remove_method [range_id]", "Removes a range from the calculator"),
    ("update_range [range_id] [method/price/range] [value] ",
     "Updates a range from the calculator"),
    ("startgiveaway Time Rank Winners Prize", "Starts a giveaway.\nTime must be like: Number [days/hours/minutes]\nExample: 7 days"),
    ("startraffle Prize Spots Price", "Starts a raffle"),
    ("addraffle User Slot1/Slot2/...","Adds participant to raffle"),
    ("drawraffle", "Ends raffle and selects a winner")
]

role = list(map(
    lambda a: int(a),
    environ.get("ROLE_ID").split(",")
))


class HelpCommands(commands.Cog):

    @commands.command(name="help", aliases=["h"])
    async def help(self, ctx):
        def new_embed(title):
            new_embed = discord.Embed(
                title=f"{title} (Command Prefix:`{ctx.prefix}`)", color=0xb9ff99)
            return new_embed

        def add_commands_to_embed(embed, command_list, prefix):
            for command, description in command_list:
                embed.add_field(name=f"`{prefix}{command}`",
                                value=description, inline=False)

        arguments = ctx.message.content.split()[1:]
        customer_embed = new_embed(title="Commands")
        if len(arguments) > 0 and arguments[0] == "staff":
            add_commands_to_embed(
                customer_embed, staff_commands_help, ctx.prefix)
        else:
            add_commands_to_embed(
                customer_embed, commands_help, ctx.prefix)
        await ctx.send(embed=customer_embed)


def setup(bot: commands.Bot):
    bot.remove_command("help")
    bot.add_cog(HelpCommands(bot))
