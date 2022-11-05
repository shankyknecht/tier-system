from DatabaseCon import DatabaseCon
from Models import RaffleTicket
from typing import List


class RaffleManagement:
    _instance = None
    _database_con: DatabaseCon = DatabaseCon.get_instance()

    @staticmethod
    def get_instance():
        if RaffleManagement._instance is None:
            RaffleManagement()
        return RaffleManagement._instance

    def __init__(self):
        if RaffleManagement._instance is not None:
            return
        RaffleManagement._instance = self

    def is_slot_available(self, slot_number):
        return self._database_con.is_slot_available(slot_number)

    def place_ticket(self, slot_number, customer_id):
        return self._database_con.place_ticket(slot_number, customer_id)

    def place_multiple_tickets(self, slot_numbers, customer_id):
        return self._database_con.place_multiple_tickets(slot_numbers, customer_id)

    def get_random_winner_ticket(self) -> RaffleTicket:
        return self._database_con.get_random_winner_ticket()

    def clear_raffle_tickets(self):
        self._database_con.clear_raffle_tickets()

    def get_all_tickets(self) -> List[RaffleTicket]:
        return self._database_con.get_all_tickets()
