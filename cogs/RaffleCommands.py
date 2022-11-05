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
from RaffleManagement import RaffleManagement
from PointsManagement import PointsManagement
from CogUtils import get_user_id
import time
import traceback

rm = RaffleManagement()
pm = PointsManagement()

role = list(map(
    lambda a: int(a),
    environ.get("ROLE_ID").split(",")
))

channel_id_for_raffle = int(environ.get("CHANNEL_FOR_RAFFLE"))

raffle_message = """

@everyone @Bronze 
Are you feeling lucky?
Join this raffle for a chance at a `{}`
One ticket is {}M and you can buy up to 4 tickets.
⭐raffle-tickets⭐ 
"""

winner_message = """
@Bronze @Raffle Participant 
pepelightsaber RAFFLE ALERT!!!pepelightsaber 

Congratz <@{}> on winning the "{}" raffle!@!@! confettiflash 

Please open a ticket in #⭐raffle-tickets⭐ to receive your prize.
You have 48 hours to claim your prize!
"""


class RaffleCommands(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.is_raffle_running = False
        self.price_per_spot = 0
        self.spots = 0
        self.prize_name = ""
        self.raffle_message: Optional[discord.Message] = None

    @commands.Cog.listener()
    async def on_ready(self):
        self.guild: discord.Guild = self.bot.guilds[0]
        self.channel_for_raffle: discord.TextChannel = self.bot.get_channel(
            channel_id_for_raffle)

    @commands.has_any_role(*role)
    @commands.command()
    async def startraffle(self, ctx: commands.Context):
        arguments = ctx.message.content.split()[1:]
        if len(arguments) < 3:
            await ctx.send("Not enough arguments. Required: [Item/Prize] [Number of Spots] [Price per Spot]")
            return

        if self.is_raffle_running:
            await ctx.send(f"There's a raffle already taking place! Use `{str(ctx.prefix)}drawraffle` to finish it.")
            return

        self.price_per_spot = float(
            arguments[-1].replace("m", "").replace("M", ""))
        self.spots = int(arguments[-2])
        self.prize_name = " ".join(arguments[:-2])

        self.is_raffle_running = True
        await ctx.send(f"Successfully started a raffle. \nPrize: `{self.prize_name}`. \nSpots: `{self.spots}`. \nPrize per spot `{self.price_per_spot}`.")
        await self.show_current_spots(ctx)

    @commands.has_any_role(*role)
    @commands.command()
    async def addraffle(self, ctx: commands.Context):

        try:

            if not self.is_raffle_running:
                raise Exception("Raffle is not running")

            arguments = ctx.message.content.split()[1:]

            user = ctx.message.mentions[0]
            usertag = str(user)

            slots = arguments[1:]
            slot_numbers = []

            if len(slots) > 4:
                raise Exception("You can only place a maximum of 4 tickets!")

            for slot in slots:
                slot_number = int(slot)

                slot_numbers.append(slot_number)
                if slot_number > self.spots or slot_number < 1:
                    raise Exception(
                        f"You can only place tickets in spots between 1 and {self.spots}")

            customer = pm.get_customer_by_tag(usertag)
            rm.place_multiple_tickets(slot_numbers, customer.customer)

            print(customer, slot_numbers)

            await ctx.send(f"Successfully placed tickets: {','.join(slots)}")
            await self.show_current_spots(ctx)

        except Exception as e:
            await ctx.send(f"Error: {str(e)}")
            print(traceback.format_exc())
            return

    @commands.has_any_role(*role)
    @commands.command()
    async def drawraffle(self, ctx: commands.Context):
        if not self.is_raffle_running:
            await ctx.send(f"No raffle is taking place. Use `{str(ctx.prefix)}startraffle` to start a raffle.")
            return

        self.is_raffle_running = False

        if len(rm.get_all_tickets()) == 0:
            await ctx.send("No one entered the raffle. No winners will be drawn.")
            return

        # Select winner
        winner_ticket = rm.get_random_winner_ticket()
        winner_name = winner_ticket.get_ticket_owner_name()
        winner_ticket_number = winner_ticket.ticket_number

        rm.clear_raffle_tickets()

        # Display winner
        await ctx.send(f"Winner Ticket: {int(winner_ticket_number)}\nWinner Name: {winner_name}")

        await self.send_or_update_message(ctx, content=winner_message.format(await get_user_id(self, ctx, winner_name), self.prize_name))

        self.is_raffle_running = False
        self.price_per_spot = 0
        self.spots = 0
        self.prize_name = ""
        self.raffle_message: Optional[discord.Message] = None

    @commands.command(hidden=True)
    async def show_current_spots(self, ctx: commands.Context):
        tickets_as_dict = dict()
        for i in range(1, self.spots + 1):
            tickets_as_dict[i] = ""

        for t in rm.get_all_tickets():
            tickets_as_dict[t.ticket_number] = t.get_ticket_owner_name()

        positions = []

        for (k, v) in tickets_as_dict.items():
            if v != "":
                s = f"{k}. <@{await get_user_id(self, ctx, v)}>"
            else:
                s = f"{k}."
            positions.append(s)

        participants = "\n".join(positions)
        result_text = raffle_message.format(
            self.prize_name, self.price_per_spot) + "\n\n\n" + participants
        await self.send_or_update_message(ctx, content=result_text)

    @commands.command(hidden=True)
    async def send_or_update_message(self, ctx: commands.Context, **kwargs):
        if self.raffle_message is None:
            self.raffle_message = await self.channel_for_raffle.send(**kwargs)
        else:
            await self.raffle_message.edit(**kwargs)


def setup(bot: commands.Bot):
    bot.add_cog(RaffleCommands(bot))
