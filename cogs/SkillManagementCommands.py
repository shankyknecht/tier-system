import asyncio
from datetime import datetime
from typing import List, Tuple
import discord
from discord.ext import commands
from discord import Embed
from dotenv.main import load_dotenv
from os import environ
from random import randint
from tabulate import tabulate
from SkillManagement import SkillManagement
import time
import traceback

sm = SkillManagement()

role = list(map(
    lambda a: int(a),
    environ.get("ROLE_ID").split(",")
))


class SkillManagementCommands(commands.Cog):
    @commands.has_any_role(*role)
    @commands.command(name="add_calc")
    async def add_calc(self, ctx: commands.Context):
        """
melee
Crabs 1-60: 45gp/xp
Crabs 60-99: 22gp/xp
NMZ 60-99: 18gp/xp

ranging
Crabs 1-60: 45gp/xp
MM1 1-99: 20gp/xp
MM2 1-99: 11gp/xp
.add_calc [skill] [start]-[finish] [amount]gp/xp [method_name]
        """
        arguments = ctx.message.content.split()[1:]
        if len(arguments) < 4:
            await ctx.send("Not enough arguments.")
            return

        skill = sm.get_skill_by_name_or_alias(
            arguments[0])

        start_finish = arguments[1].split('-')

        rate = arguments[2].replace("gp/xp", "")

        method_name = " ".join(arguments[3:])
        start = 0
        end = 0
        try:

            start = int(start_finish[0])
            end = int(start_finish[1])
            rate = float(rate)
            sm.add_new_range(skill, start, end, rate, method_name)
            await ctx.send("Sucessfully added a new method!")

        except Exception as e:
            await ctx.send(f"Error: {e}")
            traceback.print_exc()

    @commands.has_any_role(*role)
    @commands.command(name="list_methods")
    async def list_methods(self, ctx: commands.Context):

        arguments = ctx.message.content.split()[1:]
        if len(arguments) != 1:
            await ctx.send("Not enough arguments. You must input the skill name.")
            return

        skill = sm.get_skill_by_name_or_alias(
            arguments[0])
        ranges = sm.get_skill_ranges_for_skill(skill)

        embed = discord.Embed(color=0x99FB99, title=f"Methods for {skill.name}",
                              type='rich')

        headers = ["ID", "Method", "Range", "Price"]
        table = []
        for r in ranges:
            table.append([
                r.skill_range_id,
                r.method_name,
                f"{r.start_level}-{r.end_level}",
                f"{int(r.rate)}gp/xp"
            ])

        await ctx.send(embed=embed)
        tablulated = tabulate(table, headers=headers, tablefmt="pretty")
        await ctx.send(f"```\n{tablulated}\n```")

    @commands.has_any_role(*role)
    @commands.command(name="remove_method")
    async def remove_method(self, ctx: commands.Context):
        arguments = ctx.message.content.split()[1:]
        if len(arguments) < 1:
            await ctx.send("Not enough arguments. You must the skill range id.")
            return
        sm.delete_range(arguments[0])
        await ctx.send("Sucessfully removed a method!")

    @commands.has_any_role(*role)
    @commands.command(name="update_method")
    async def update_method(self, ctx: commands.Context):
        arguments = ctx.message.content.split()[1:]
        if len(arguments) < 3:
            await ctx.send("Not enough arguments."
                           "You must input the skill range id, the field to change and the new value.")
            return
        try:
            sm.update_range(arguments[0], arguments[1], arguments[2])
        except Exception as e:
            await ctx.send(f"Error: {e}")


def setup(bot: commands.Bot):
    bot.add_cog(SkillManagementCommands(bot))
