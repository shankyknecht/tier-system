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

role = list(map(
    lambda a: int(a),
    environ.get("ROLE_ID").split(",")
))


class PointsCommands(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.has_any_role(*role)
    @commands.command(name="add_points", aliases=["add"])
    async def add_points(self, ctx):
        await self.set_points(ctx, "add")

    @commands.has_any_role(*role)
    @commands.command(name="remove_points", aliases=["remove"])
    async def remove_points(self, ctx):
        await self.set_points(ctx, "remove")

    @commands.has_any_role(*role)
    @commands.command(name="update_points", aliases=["update"])
    async def update_points(self, ctx):
        await self.set_points(ctx, "update")

    @commands.has_any_role(*role)
    @commands.command(name="reset")
    async def reset_points(self, ctx):
        await self.set_points(ctx, "reset")

    @commands.command(hidden=True)
    async def set_points(self, ctx: commands.Context, transtype):
        arguments = ctx.message.content.split()[1:]
        if len(arguments) != 2 and not transtype == "reset":
            await ctx.send("This command requires 2 arguments.")
            return
        try:

            staff_discord_id = ctx.author.id
            staff_discord_tag = f"{ctx.author.name}#{ctx.author.discriminator}"

            user = ctx.message.mentions[0]
            usertag = str(user)
            user_tag_string = user_id_to_chat_tag(ctx.message.mentions[0].id)
            if not transtype == "reset":
                quantity = int(ctx.message.content.split()[2])
            else:
                quantity = 0

            if quantity < 0:
                raise Exception("Negative number")

            temp_string = ""

            previous_ammount = self.bot.points_management.get_customer_points(
                usertag)
            self.bot.points_management.update_customer_points(
                usertag, quantity, staff_discord_tag, staff_discord_id, transtype)
            if transtype == "add":
                temp_string = f"Added {quantity} points to {user_tag_string}."
            elif transtype == "remove":
                temp_string = f"Took {quantity} points from {user_tag_string}."
            elif transtype == "reset":
                temp_string = f"Reset {user_tag_string} points back to `0`."
            else:
                temp_string = f"Set {user_tag_string} points to `{quantity}`."

            current_ammount = self.bot.points_management.get_customer_points(
                usertag)

            await ctx.send(temp_string)
            await ctx.send(f"Previous ammount was `{previous_ammount}` points and now is `{current_ammount}` points.")
            await self.update_user_roles(ctx, current_ammount)

        except Exception as e:
            await ctx.send(f"Error while using the `{ctx.command.name}` command: `{str(e)}`\nUsage: `{ctx.prefix}{ctx.command.name} User Ammount`")
            print(traceback.format_exc())

    @commands.has_any_role(*role)
    @commands.command(name="points_check", aliases=["pcheck"])
    async def points_check(self, ctx):
        user_tag = str(ctx.message.mentions[0])
        await self.send_points_display(ctx, user_tag)

    @commands.command(name="points", aliases=["p"])
    async def get_own_points(self, ctx):
        user_tag = f"{ctx.author.name}#{ctx.author.discriminator}"
        await self.send_points_display(ctx, user_tag)

    @commands.command(name="highscores", aliases=["hs"])
    async def highscores(self, ctx):
        top_10 = self.bot.points_management.get_top_10()
        embed = discord.Embed(title="Points Hiscores", color=0x99FB59)
        for i in range(len(top_10)):
            embed.add_field(
                name=f"{i + 1} - **{top_10[i].discord_tag}**",
                value=f"`{top_10[i].points}` points",
                inline=False
            )
        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    async def send_points_display(self, ctx, user_tag):
        embed = discord.Embed(color=0x99FB59)
        embed.add_field(
            name=f":scroll: **{user_tag}'s points: **`{self.bot.points_management.check_customer_points(user_tag)}`", value='\u200b', inline=False)
        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    async def update_user_roles(self, ctx: commands.Context, current_points):
        user: discord.Member = ctx.message.mentions[0]
        user_previous_roles = list(map(lambda r: r.name, user.roles))

        under_roles, above_roles = self.bot.role_management.get_under_and_above_roles(
            current_points)

        print(under_roles, above_roles)
        await user.add_roles(*under_roles)
        await user.remove_roles(*above_roles)

        user_current_roles = list(map(lambda r: r.name, user.roles))
        added_or_removed_str = ""
        from_or_to = ""
        if len(user_previous_roles) < len(user_current_roles):
            added_or_removed_str = "Added"
            from_or_to = "to"
        else:
            added_or_removed_str = "Removed"
            from_or_to = "from"

        differential_roles = list(
            set(user_previous_roles) ^ set(user_current_roles))

        print(differential_roles)
        if len(differential_roles) > 0:
            self.bot.role_management.sort_role_names(differential_roles)
            added_roles_string = ",".join(
                list(map(lambda a: f"`{a}`", differential_roles)))
            user_tag_string = user_id_to_chat_tag(user.id)
            await ctx.send(f"{added_or_removed_str} the following roles {from_or_to} {user_tag_string}: {added_roles_string}")

    @commands.has_any_role(*role)
    @commands.command(name="reset_all")
    async def reset_all(self, ctx: commands.Context):
        current_msg = await ctx.send("Resetting all points/roles.")
        all_role_objs = self.bot.role_management.get_all_role_objs()
        await asyncio.gather(*[member.remove_roles(*all_role_objs) for member in ctx.guild.members])
        num_rows_deleted = self.bot.points_management.reset_all()
        await ctx.send("Done resetting.")
        await ctx.send(f"Reset {num_rows_deleted} customer points!")

    @commands.command(name="ranks")
    async def ranks(self, ctx: commands.Context):

        roles_names_and_points = self.bot.role_management.get_roles_names_and_points()

        new_embed = discord.Embed(
            title=f"**Roles**", color=0xb9ff99)

        for role_name, role_value in roles_names_and_points:
            new_embed.add_field(name=f"**{role_name}**",
                                value=f"`{role_value}` points", inline=False)

        await ctx.send(embed=new_embed)

    @commands.has_any_role(*role)
    @commands.command(name="staff_points", aliases=["sp"])
    async def staff_points(self, ctx):
        if len(ctx.message.mentions) == 1:
            user = ctx.message.mentions[0]
            usertag = str(user)
            total_points = self.bot.points_management.get_total_points_staff(
                usertag)

            embed = discord.Embed(color=0x99FB59)
            embed.add_field(
                name=f":bar_chart:  **{usertag}'s total added points: **`{total_points}`", value='\u200b', inline=False)
            await ctx.send(embed=embed)

        else:
            tags_and_points = self.bot.points_management.get_all_total_points()

            new_embed = discord.Embed(
                title=f":bar_chart: **Staff Total Points** ", color=0xb9ff99)

            for tag, points in tags_and_points:
                new_embed.add_field(name=f"**{tag}**",
                                    value=f"`{points}` points", inline=False)

            await ctx.send(embed=new_embed)


def user_id_to_chat_tag(author_id):
    return f"<@{author_id}>"


def setup(bot: commands.Bot):
    bot.add_cog(PointsCommands(bot))
