from DatabaseCon import DatabaseCon
from Models import RaffleTicket, Customer

from typing import List
from random import choice


class GiveawayManagement:
    _instance = None
    _database_con: DatabaseCon = DatabaseCon.get_instance()

    @staticmethod
    def get_instance():
        if GiveawayManagement._instance is None:
            GiveawayManagement()
        return GiveawayManagement._instance

    def __init__(self):
        if GiveawayManagement._instance is not None:
            return
        GiveawayManagement._instance = self
        # TODO: when starting it should ask the database if there's any giveaway going
        # and get the current

    def start_giveaway(self, endtime, prize_name, rank_id):
        return self._database_con.start_giveaway(endtime, rank_id, prize_name)

    def stop_giveaway(self, giveaway_id):
        self._database_con.stop_giveaway(giveaway_id)

    def draw_giveaway(self, giveaway_id) -> Customer:
        giveaway = self._database_con.get_giveaway_by_id(giveaway_id)
        entries = self._database_con.get_giveaway_entries(giveaway_id)
        winner_entry = choice(entries)
        giveaway.winner_id = winner_entry.get_entry_customer().customer
        self.stop_giveaway(giveaway_id)
        return winner_entry.get_entry_customer()

    def add_entry_to_giveaway(self, giveaway_id, customer_id):
        self._database_con.add_entry_to_giveaway(giveaway_id, customer_id)

    def get_giveaway_entries(self, giveaway_id):
        return self._database_con.get_giveaway_entries(giveaway_id)
