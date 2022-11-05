import asyncio
from typing import Optional
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
import datetime
from CogUtils import user_tag_from_author
from GiveawayManagement import GiveawayManagement
from PointsManagement import PointsManagement
from random import choices

gm = GiveawayManagement()
pm = PointsManagement()


role = list(map(
    lambda a: int(a),
    environ.get("ROLE_ID").split(",")
))


class GiveawayView(discord.ui.View):
    @discord.ui.button(label='JOIN!', emoji="🎉", style=discord.ButtonStyle.green)
    async def button_yes_callback(self, button, interaction: discord.Interaction):
        usertag = user_tag_from_author(interaction.user)

        print(interaction.user.roles)
        if (self.rank not in [x.name for x in interaction.user.roles]) and (self.rank not in [x.id for x in interaction.user.roles]):
            await interaction.response.send_message(content="You don't have the required rank to participate!", ephemeral=True)
            return

        try:
            await self.join_giveaway(usertag)
            await self.update_entries()
            await interaction.response.send_message(content="Successfully joined the giveaway!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(content=f"Error {str(e)}", ephemeral=True)

    def __init__(self, join_giveaway, update_entries, endgiveaway, rank, finish_timeout):
        self.join_giveaway = join_giveaway
        self.update_entries = update_entries
        self.end_giveaway = endgiveaway
        print(rank)
        try:
            self.rank = int(rank)
        except Exception:
            self.rank = rank
        super().__init__(timeout=10)

    async def finish(self, interaction):
        self.clear_items()
        self.stop()
        await self.end_giveaway()

    async def on_timeout(self):
        self.clear_items()
        self.stop()
        await self.end_giveaway()


class GiveawayCommands(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # startgiveaway 20 min @everyone prize...
    @commands.has_any_role(*role)
    @commands.command()
    async def startgiveaway(self, ctx: commands.Context):
        arguments = ctx.message.content.split()[1:]
        if len(arguments) < 5:
            await ctx.send("Not enough arguments. Required: [endtime] [rank] [number of winners] [prizename] ")
            return

        time_amount = arguments[0]
        time_time = arguments[1]
        rank = arguments[2]
        number_of_winners = int(arguments[3])
        prize = " ".join(arguments[4:])

        endtime, seconds_to_run = time_string_to_endtime(
            time_amount, time_time)

        giveaway_id = gm.start_giveaway(endtime, prize, rank)

        async def join_giveaway(usertag):
            customer = pm.get_customer_by_tag(usertag)
            gm.add_entry_to_giveaway(giveaway_id, customer.customer)

        m: discord.Message = None

        running = True

        giveaway_template = """
        Giveaway!

   `Prize        :` {}
   `No of Winners:` {}
   `Rank         :` {}
   `Draws in     :` {} minutes

        **CLICK ON THE BUTTON BELLOW!**
        """

        def template_to_text(prize, number_of_winners, rank, ends_minutes):
            if "everyone" in rank:
                rank_tag = "@everyone"
            else:
                rank_tag = "<@&{}>".format(rank)
            return giveaway_template.format(
                prize, number_of_winners, rank_tag, ends_minutes)

        async def update_entries():
            await m.edit(content=template_to_text(prize, number_of_winners, rank, minutes_to_finish(endtime)))

        async def update_entries_loop():
            while running:
                await update_entries()
                time.sleep(10)

        task = asyncio.create_task(update_entries_loop())

        async def end_giveaway():
            entries = gm.get_giveaway_entries(giveaway_id)
            winners = choices(entries, k=number_of_winners)
            winners_names = [x.get_entry_customer_name() for x in winners]
            text = ""
            if number_of_winners == 1:
                text = f"{winners_names[0]}"
            else:
                winners_text = ", ".join(winners_names)
                text = f"{winners_text}"

            new_embed = discord.Embed(
                title=f"Giveaway Finished", color=0xb9ff99)
            new_embed.add_field(value=f"{prize}", name=f"Prize", inline=False)
            new_embed.add_field(value=text, name=f"Winner(s)", inline=False)

            await m.edit(embed=new_embed, view=None)
            running = False

            task.cancel()

        await ctx.message.delete()
        m: discord.Message = await ctx.send(content=template_to_text(prize, number_of_winners, rank, minutes_to_finish(endtime)), view=GiveawayView(join_giveaway, update_entries, end_giveaway, rank.removeprefix("<@&").removesuffix(">"), 30))
        await update_entries()


# Returns endtime and the amount of seconds that the giveaway will be up
def time_string_to_endtime(amount, t):
    amount = float(amount)
    delta = datetime.timedelta()
    if t == "days":
        delta = datetime.timedelta(days=amount)
    elif t == "hours":
        delta = datetime.timedelta(hours=amount)
    elif t == "minutes" or t == "min":
        delta = datetime.timedelta(minutes=amount)
    endtime = datetime.datetime.now() + delta
    return (endtime, delta.total_seconds())


def minutes_to_finish(endtime):
    return int((endtime - datetime.datetime.now()).total_seconds() / 60)


def setup(bot: commands.Bot):
    bot.add_cog(GiveawayCommands(bot))
