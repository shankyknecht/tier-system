from typing import List
import discord


class RoleManagement:
    _instance = None

    roles_to_values = {
        "Steel": (None, 1),
        "Black": (None, 100),
        "Mithril": (None, 250),
        "Adamant": (None, 500),
        "Rune": (None, 1000),
        "Dragon": (None, 2000),

    }

    @staticmethod
    def get_instance():
        if RoleManagement._instance is None:
            RoleManagement()
        return RoleManagement._instance

    def __init__(self):
        if RoleManagement._instance is not None:
            return
        RoleManagement._instance = self

    def get_roles_names_and_points(self):
        result = []
        for role_name, (role_obj, role_ammount) in self.roles_to_values.items():
            result.append((role_name, role_ammount))
        return result

    def load_roles(self, roles: List[discord.Role]):
        for role in roles:
            if role.name in self.roles_to_values:
                _, ammount = self.roles_to_values[role.name]
                self.roles_to_values[role.name] = (role, ammount)

    def get_all_role_objs(self):
        result = []
        for role_name, (role_obj, role_ammount) in self.roles_to_values.items():
            result.append(role_obj)
        return result

    def get_under_and_above_roles(self, ammount):
        under_roles = []  # Roles that a user has
        above_roles = []  # Roles that a user doesn't have yet
        for role_name, (role_obj, role_ammount) in self.roles_to_values.items():
            if role_ammount <= ammount:
                under_roles.append(role_obj)
            else:
                above_roles.append(role_obj)
        return under_roles, above_roles

    def sort_role_names(self, role_names: List[str]):
        def sort_key(name):
            value = self.roles_to_values[name][1]
            print(name, value)
            return value
        role_names.sort(key=sort_key)
