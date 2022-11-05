import asyncio
from datetime import datetime
from typing import List, Tuple
import discord
from discord.ext import commands
from discord import Embed
from dotenv.main import load_dotenv
from os import environ
from random import randint
from SkillManagement import SkillManagement
from Models import SkillRanges, SkillAliases, Skills
import time
import traceback
from CogUtils import to_millions

sm = SkillManagement()

role = list(map(
    lambda a: int(a),
    environ.get("ROLE_ID").split(",")
))


class SkillCommands(commands.Cog):

    @commands.command(name="skill", aliases=sm.get_skill_names_and_aliases())
    async def skill(self, ctx: commands.Context):
        arguments = ctx.message.content.split()
        skill_query = arguments[0].strip(str(ctx.prefix))

        try:
            skill = sm.get_skill_by_name_or_alias(skill_query)
        except Exception:
            await ctx.send("Error: Skill not found")

        if len(arguments) == 1:
            await self.show_skill_methods(ctx, skill)
            return

        start_end = arguments[1].split("-")
        if len(start_end) == 2:
            await self.calculate_between_range(ctx, skill, start_end)
        else:
            await ctx.send("Error: You provided a wrong range."
                           "You either provide a range, like `30-92` or no range at all.")

    @commands.command(hidden=True)
    async def calculate_between_range(self, ctx: commands.Context, skill: Skills, start_end):
        start, end = start_end
        try:
            start = int(start)
            end = int(end)

            if 0 < start > 99 or 0 < end > 99 and start > end:
                raise Exception()

        except Exception:
            await ctx.send("Error: You provided a wrong range."
                           "Ranges must be valid numbers, between 1 and 99, and start must be lower than end.")
            return

        total_xp = sm.from_to_xp(start, end)
        embed = discord.Embed(color=0x99FB59, title=f"Price for {skill.name.capitalize()}",
                              type='rich', url=Embed.Empty, description=f"Between {start} and {end} - Total XP: {to_millions(total_xp)}M xp")

        for method_name, method_tree in sm.calculator_method_wise(skill, start, end).items():
            total_price = 0
            string_lines = []

            for interval in method_tree:
                start, end, skill_range = interval
                xp_between = sm.from_to_xp(start, end)
                price_between = xp_between * skill_range.rate
                total_price = total_price + price_between

                range_string = f"{start}-{end}: {to_millions(price_between)}M"

                string_lines.append(range_string)

            string_lines.append(f"Price: {to_millions(total_price)}M")

            embed.add_field(name=method_name, value="\n".join(
                string_lines), inline=False)

        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    async def show_skill_methods(self, ctx: commands.Context, skill: Skills):
        embed = discord.Embed(color=0x99FB59, title=f"Methods and prices for {skill.name.capitalize()}",
                              type='rich')

        for method_name, method_tree in sm.calculator_method_wise(skill, 0, 99).items():
            string_lines = []
            start_levels = []
            end_levels = []

            for interval in method_tree:
                start, end, skill_range = interval

                start_levels.append(start)
                end_levels.append(end)

                rate = skill_range.rate

                range_string = f"{start}-{end}: {int(rate)}gp/xp"

                string_lines.append(range_string)

            embed.add_field(name=f"{method_name} {min(start_levels)}-{max(end_levels)}", value="\n".join(
                string_lines), inline=False)

        await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(SkillCommands(bot))
