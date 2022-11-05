from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.sql.elements import Extract
from sqlalchemy.sql import functions
from datetime import date, datetime, timedelta
from sqlalchemy.sql.expression import func
from operator import and_, or_
from typing import List, Tuple, Union
from sqlalchemy.engine.create import create_engine
from sqlalchemy.orm.session import Session, sessionmaker
from sqlalchemy import extract
from Models import Base, Customer, Staff, TransactionLog, SkillRanges, SkillAliases, Skills, RaffleTicket, GiveawayEntries, Giveaways
from random import choice


class DatabaseCon:
    _instance = None
    _session: Session

    @staticmethod
    def get_instance():
        if DatabaseCon._instance is None:
            DatabaseCon()
        return DatabaseCon._instance

    def __init__(self):
        if DatabaseCon._instance is not None:
            return
        DatabaseCon._instance = self

        self._engine = create_engine("sqlite:///database.db")

        Base.metadata.create_all(bind=self._engine)
        Session = sessionmaker(bind=self._engine)

        self._session = scoped_session(Session)

    def create_customer_by_tag(self, usertag):
        self._session.add(
            Customer(discord_tag=usertag, points=0)
        )
        self._session.commit()

    def get_customer_by_tag(self, usertag) -> Customer:
        result_from_db = (
            self._session
            .query(Customer)
            .filter(Customer.discord_tag == usertag)
        ).all()
        if len(result_from_db) == 0:
            self.create_customer_by_tag(usertag)
            return self.get_customer_by_tag(usertag)
        else:
            return result_from_db[0]

    def get_customer_points(self, usertag):
        return self.get_customer_by_tag(usertag).points

    def update_customer_points(self, usertag, points_change, staff_discord_tag, staff_discord_id, movement_type="update"):

        customer = self.get_customer_by_tag(usertag)
        transaction_point_change = 0

        new_points_value = 0
        if movement_type == "add":
            new_points_value = customer.points + points_change
            transaction_point_change = points_change

        elif movement_type == "remove":
            new_points_value = customer.points - points_change
            transaction_point_change = -points_change

        elif movement_type == "reset":
            new_points_value = 0
            transaction_point_change = -customer.points
        else:
            new_points_value = points_change
            transaction_point_change = points_change - customer.points

        if new_points_value < 0:
            new_points_value = 0

        customer.points = new_points_value

        newTransaction = TransactionLog(
            staff_id=self.get_staff(
                discord_tag=staff_discord_tag, discord_id=staff_discord_id).staff_id,
            customer_id=customer.customer,
            movement_date=datetime.now(),
            movement_type=movement_type,
            amount=transaction_point_change
        )
        self._session.add(newTransaction)

        self._session.commit()

    def get_top_10(self) -> List[Customer]:

        result = (self._session.query(Customer)
                  .order_by(Customer.points.desc())
                  .limit(10)
                  .all()
                  )

        return result

    def get_all_discord_tags(self):
        result_from_db = (
            self._session
            .query(Customer)
        ).all()
        return list(map(lambda a: a.discord_tag, result_from_db))

    def reset_all(self):
        num_rows_deleted = self._session.query(Customer).delete()
        self._session.commit()
        return num_rows_deleted

    def create_staff(self, discord_tag, discord_id):
        self._session.add(
            Staff(discord_tag=discord_tag, discord_id=discord_id)
        )
        self._session.commit()

    def get_all_staff(self):
        result_from_db = (
            self._session
            .query(Staff)
        ).all()
        return result_from_db

    def get_staff(self, staff_id=-1, discord_tag="", discord_id=-1):
        filter = True == True

        if staff_id != -1:
            filter = Staff.staff_id == staff_id

        elif discord_tag != "":
            filter = Staff.discord_tag == discord_tag
        elif discord_id != -1:
            filter = Staff.discord_id == discord_id
        else:
            raise Exception("Not possible to find staff member!")

        result_from_db = (
            self._session
            .query(Staff)
            .filter(filter)
        ).all()
        if len(result_from_db) == 0:
            if discord_tag != "" and discord_id != -1:
                self.create_staff(discord_tag, discord_id)
                return self.get_staff(staff_id, discord_tag, discord_id)
            else:
                raise Exception("Not possible to create staff member!")

        else:
            return result_from_db[0]

    def get_total_points_staff(self, staff_id=-1, discord_tag="", discord_id=-1):
        staff = self.get_staff(staff_id=staff_id,
                               discord_tag=discord_tag, discord_id=discord_id)
        cursor = self._session.query(func.sum(TransactionLog.amount)).filter(
            TransactionLog.staff_id == staff.staff_id)
        total = cursor.scalar()
        return int(total)

    def get_all_total_points(self) -> List[Tuple[str, int]]:
        all_staff = self.get_all_staff()

        all_total_points = list(
            map(lambda staff: (staff.discord_tag,
                self.get_total_points_staff(staff_id=staff.staff_id)), all_staff)
        )
        all_total_points.sort(key=(lambda a: a[1]), reverse=True)
        return all_total_points

    def get_skills(self) -> List[Skills]:
        return (
            self._session
            .query(Skills)
        ).all()

    def get_skill_aliases(self) -> List[Skills]:
        return (
            self._session
            .query(SkillAliases)
        ).all()

    def get_skill_ranges(self) -> List[SkillRanges]:
        return (
            self._session
            .query(SkillRanges)
        ).all()

    def get_skill_range(self, skill) -> List[SkillRanges]:
        result_from_db = (
            self._session
            .query(SkillRanges)
            .filter(SkillRanges.skill == skill)
        ).all()

        return result_from_db

    def get_skill_range_by_id(self, skill_range_id):
        return (
            self._session
            .query(SkillRanges)
            .filter(SkillRanges.skill_range_id == skill_range_id)
        ).first()

    def insert_new_range(self, skill, start, end, rate, method_name):
        skill_id = -1

        if isinstance(skill, Skills):
            skill_id = skill.skill_id
        elif isinstance(skill, int):
            skill_id = skill

        if skill_id == -1:
            raise Exception("Invalid skill")

        self._session.add(
            SkillRanges(skill_id=skill_id, start_level=start,
                        end_level=end, method_name=method_name, rate=rate)
        )
        self._session.commit()

    def delete_range(self, skill_range_id):
        _ = (
            self._session
            .query(SkillRanges)
            .filter(SkillRanges.skill_range_id == skill_range_id)
        ).delete()

    def clear_raffle_tickets(self):
        for t in self.get_all_tickets():
            t.customer = None
            t.customer_id = -1
            self._session.query(RaffleTicket).filter(
                RaffleTicket.ticket_number == t.ticket_number).delete()
            self._session.commit()

    def get_slot_owner(self, ticket_number):
        slot = (
            self._session
            .query(RaffleTicket)
            .filter(RaffleTicket.ticket_number == ticket_number)
        ).first()

        if slot is None:
            return None
        else:
            return slot.customer_id

    def is_slot_available(self, slot_number):
        return (self.get_slot_owner(slot_number) is None)

    def place_ticket(self, slot_number, customer_id):
        if self.is_slot_available(slot_number):
            self._session.add(
                RaffleTicket(ticket_number=slot_number,
                             customer_id=customer_id)
            )
            self._session.commit()
        else:
            raise Exception(f"Slot {slot_number} is not available")

    def place_multiple_tickets(self, slot_numbers, customer_id):
        if all([self.is_slot_available(slot_number) for slot_number in slot_numbers]):
            for slot_number in slot_numbers:
                self.place_ticket(slot_number, customer_id)
                print(f"Slot {slot_number}")
        else:
            for slot_number in slot_numbers:
                if not self.is_slot_available(slot_number):
                    raise Exception(f"Slot {slot_number} is not available")
            print("IMPOSSIBLE")

    def get_all_tickets(self) -> List[RaffleTicket]:
        all_tickets: List[RaffleTicket] = (
            self._session.query(RaffleTicket).all())

        all_tickets.sort(key=(lambda r: r.ticket_number))

        return all_tickets

    def get_random_winner_ticket(self) -> RaffleTicket:
        return choice(self.get_all_tickets())

    def start_giveaway(self, endtime, rank_id, prize_name) -> int:
        new_giveaway = Giveaways(
            endtime=endtime, rank_id=rank_id, prize_name=prize_name, winner_id=-1, running=True)
        self._session.add(new_giveaway)
        self._session.commit()

        return new_giveaway.giveaway_id

    def get_giveaway_by_id(self, giveaway_id) -> Giveaways:
        return (
            self._session
            .query(Giveaways)
            .filter(Giveaways.giveaway_id == giveaway_id)
        ).first()

    def add_entry_to_giveaway(self, giveaway_id, customer_id):
        customer_entries = (
            self._session
            .query(GiveawayEntries)
            .filter(and_(GiveawayEntries.giveaway_id == giveaway_id, GiveawayEntries.customer_id == customer_id))
        ).all()
        if len(customer_entries) > 0:
            raise Exception("Customer already joined this giveaway")

        new_giveaway = GiveawayEntries(
            giveaway_id=giveaway_id, customer_id=customer_id)
        self._session.add(new_giveaway)
        self._session.commit()

    def get_giveaway_entries(self, giveaway_id) -> List[GiveawayEntries]:
        return (
            self._session
            .query(GiveawayEntries)
            .filter(GiveawayEntries.giveaway_id == giveaway_id)
        ).all()

    def stop_giveaway(self, giveaway_id):
        giveaway = self.get_giveaway_by_id(giveaway_id)
        giveaway.running = False
        self._session.commit()
