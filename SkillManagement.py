from math import floor
from DatabaseCon import DatabaseCon
from Models import Customer

from typing import List, Dict, Tuple
from Models import Skills, SkillRanges, SkillAliases
from intervaltree import Interval, IntervalTree


class InvalidSkillName(Exception):
    def __init__(self, skill_name):
        self.message = f"Invalid skill name '{skill_name}'"
        super().__init__(self.message)


class SkillManagement:
    _instance = None
    _database_con: DatabaseCon = DatabaseCon.get_instance()

    @staticmethod
    def get_instance():
        if SkillManagement._instance is None:
            SkillManagement()
        return SkillManagement._instance

    def __init__(self):
        if SkillManagement._instance is not None:
            return
        SkillManagement._instance = self

    def get_skills(self) -> List[Skills]:
        return self._database_con.get_skills()

    def get_skill_by_obj_or_id(self, skill):
        if isinstance(skill, int):
            return [x for x in self.get_skills() if x.skill_id == skill][0]
        if isinstance(skill, Skills):
            return skill

    def get_aliases(self) -> List[SkillAliases]:
        return self._database_con.get_skill_aliases()

    def get_ranges(self) -> List[SkillRanges]:
        return self._database_con.get_skill_ranges()

    def get_skill_names(self):
        return [x.name for x in self.get_skills()]

    def get_aliases_names(self):
        return [x.alias for x in self.get_aliases()]

    def get_skill_names_and_aliases(self):
        return (self.get_skill_names() + self.get_aliases_names())

    def get_skill_by_name_or_alias(self, skill_name_query: str) -> Skills:
        skill_name_query = skill_name_query.lower()

        for i in self.get_skills():
            if i.name == skill_name_query:
                return i

        for i in self.get_aliases():
            if i.alias == skill_name_query:
                return i.skill

        raise InvalidSkillName(skill_name_query)

    def get_skill_ranges_for_skill(self, skill):
        skill = self.get_skill_by_obj_or_id(skill)
        return [x for x in self.get_ranges() if x.skill_id == skill.skill_id]

    def to_reach(self, level):
        sum = 0
        for l in range(1, level):
            sum += floor(l + 300 * (2 ** (l/7)))
        return floor((1/4) * sum)

    def from_to_xp(self, level_start, level_end):
        return self.to_reach(level_end) - self.to_reach(level_start)

    def add_new_range(self, skill, start, end, rate, method_name):
        self._database_con.insert_new_range(
            skill, start, end, rate, method_name)

    def delete_range(self, skill_range_id):
        self._database_con.delete_range(skill_range_id)

    def update_range(self, skill_range_id, field, value):
        field = field.lower()
        skill_range = self._database_con.get_skill_range_by_id(skill_range_id)

        if field == "method":
            skill_range.method_name = value
        elif field == "range":
            start_end = value.split("-")
            if len(start_end) != 2:
                raise Exception(
                    "Invalid Range: You must provide a range with the following format: start-end")
            start, end = start_end
            try:
                start = int(start)
                end = int(end)
            except Exception:
                raise Exception("Invalid Range: Values must be numbers.")

            skill_range.start_level = start
            skill_range.end_level = end

        elif field == "price":
            try:
                price = float(value)
                skill_range.rate = price

            except Exception:
                raise Exception("Invalid Price: Value must be a number.")
        else:
            raise Exception("Invalid Field Name.")

        self._database_con.commit()

    def get_possible_methods(self, skill, start, end) -> List[SkillRanges]:
        skill = self.get_skill_by_obj_or_id(skill)
        return [x for x in self.get_skill_ranges_for_skill(skill) if x.end_level <= end]

    def join_ranges_by_method(self, skill) -> Dict[str, List[SkillRanges]]:
        skill = self.get_skill_by_obj_or_id(skill)

        methods = dict()

        for i in self.get_skill_ranges_for_skill(skill):
            if i.method_name in methods.keys():
                methods[i.method_name].append(i)
            else:
                methods[i.method_name] = [i]

        return methods

    def calculator_method_wise(self, skill, start, end) -> Dict[str, IntervalTree]:
        ranges_joined = self.join_ranges_by_method(skill)

        methods_calculated = dict()

        for method_name, methods in ranges_joined.items():
            t = IntervalTree()
            for i in methods:
                t.addi(i.start_level, i.end_level, i)

            t.chop(0, start)
            t.chop(end, 99)
            if len(t) != 0:
                methods_calculated[method_name] = sorted(t)

        return methods_calculated

    def get_range_attributes(self):
        return [
            "rate",
            "start_level",
            "end_level",
            "method_name",
            "description",
        ]

    def change_range(self, skill_range_id, val, key):
        if val == rate:
            skill_range.rate = float(val)
        elif val == start_level:
            skill_range.start_level = int(val)
        elif val == end_level:
            skill_range.end_level = int(val)
        elif val == method_name:
            skill_range.method_name = val
        elif val == description:
            skill_range.description = val
        if key not in self.get_range_attributes():
            raise Exception(
                f"Wrong attribute! You can only change the following `{','.join(self.get_range_attributes)}`")
        else:
            self._database_con._session.commit()


if __name__ == "__main__":
    sm = SkillManagement()
    skill = sm.get_skill_by_name_or_alias("rc")
    print(skill)
    methods_wise = sm.calculator_method_wise(skill, 30, 90)
    print(methods_wise)
    method = methods_wise["Solo Lavas"]
    print(method)
    total_price = 0
    print("\n\n")
    for interval in method:
        start, end, skill_range = interval
        xp_between = sm.from_to_xp(start, end)
        price_between = xp_between * skill_range.rate
        total_price = total_price + price_between

        print(
            f"{start} - {end} ({xp_between}xp * {skill_range.rate}gp/xp) = {total_price}")

    print(f"Total Price: {total_price}")
