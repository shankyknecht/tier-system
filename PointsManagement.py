from DatabaseCon import DatabaseCon
from Models import Customer
from typing import List


class PointsManagement:
    _instance = None
    _database_con: DatabaseCon = DatabaseCon.get_instance()

    @staticmethod
    def get_instance():
        if PointsManagement._instance is None:
            PointsManagement()
        return PointsManagement._instance

    def __init__(self):
        if PointsManagement._instance is not None:
            return
        PointsManagement._instance = self

    def get_customer_by_tag(self, usertag):
        return self._database_con.get_customer_by_tag(usertag)

    def get_customer_points(self, usertag):
        return self._database_con.get_customer_points(usertag)

    def update_customer_points(self, usertag, new_points_value, staff_discord_tag, staff_discord_id, movement_type):
        self._database_con.update_customer_points(
            usertag, new_points_value, staff_discord_tag, staff_discord_id, movement_type)

    def check_customer_points(self, usertag):
        return self.get_customer_by_tag(usertag).points

    def get_top_10(self) -> List[Customer]:
        return self._database_con.get_top_10()

    def reset_all(self):
        return self._database_con.reset_all()

    def get_all_discord_tags(self):
        return self._database_con.get_all_discord_tags()

    def get_total_points_staff(self, discord_tag):
        return self._database_con.get_total_points_staff(discord_tag=discord_tag)

    def get_all_total_points(self):
        return self._database_con.get_all_total_points()
