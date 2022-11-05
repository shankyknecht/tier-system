from typing import List, Tuple
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Sequence
from sqlalchemy.sql.sqltypes import FLOAT, Boolean, DateTime, Float
from datetime import datetime

Base = declarative_base()


class Customer(Base):
    __tablename__ = "customer"
    customer = Column(Integer, Sequence(
        "seq_street_segment_id"), primary_key=True)
    discord_tag = Column(String)
    points = Column(Integer)


class Staff(Base):
    __tablename__ = "staff"
    staff_id = Column(Integer, Sequence(
        "seq_street_segment_id"), primary_key=True)
    discord_tag = Column(String)
    discord_id = Column(Integer)


class TransactionLog(Base):
    __tablename__ = "transaction_log"
    transaction_id = Column(Integer, Sequence(
        "seq_street_segment_id"), primary_key=True)
    staff_id = Column(Integer, ForeignKey("staff.staff_id"))
    customer_id = Column(Integer, ForeignKey("customer.customer"))
    movement_date = Column(DateTime, default=datetime.utcnow())
    movement_type = Column(String)
    amount = Column(Integer)


class Skills(Base):
    __tablename__ = "skills"
    skill_id = Column(Integer, Sequence(
        "seq_street_segment_id"), primary_key=True)
    name = Column(String)
    alias = relationship(
        "SkillAliases", back_populates="skill")
    ranges = relationship(
        "SkillRanges", back_populates="skill")


class SkillAliases(Base):
    __tablename__ = "skill_aliases"
    skill_aliase_id = Column(Integer, Sequence(
        "seq_street_segment_id"), primary_key=True)
    alias = Column(String)
    skill_id = Column(Integer, ForeignKey("skills.skill_id"))
    skill = relationship(
        "Skills", back_populates="alias")


class SkillRanges(Base):
    __tablename__ = "skill_ranges"
    skill_range_id = Column(Integer, Sequence(
        "seq_street_segment_id"), primary_key=True)
    rate = Column(FLOAT)
    skill_id = Column(Integer, ForeignKey("skills.skill_id"))
    start_level = Column(Integer)
    end_level = Column(Integer)
    method_name = Column(String)
    description = Column(String)

    skill = relationship(
        "Skills", back_populates="ranges")

    def __str__(self):
        return f"[{self.skill_range_id}:{self.skill.name}:{self.method_name}: {self.start_level}-{self.end_level}]"

    def string_pretty(self):
        return f"ID:{self.skill_range_id} Method:{self.method_name}({self.skill.name}) Range:{self.start_level}-{self.end_level} Rate: {self.rate}"


class Giveaways(Base):
    __tablename__ = "giveaways"
    giveaway_id = Column(Integer, primary_key=True)
    endtime = Column(DateTime)
    rank_id = Column(Integer)
    prize_name = Column(String)
    message_id = Column(Integer)
    winner_id = Column(Integer, ForeignKey("customer.customer"))
    winner = relationship("Customer")
    running = Column(Boolean)

    def get_entry_winner(self):
        return self.customer


class GiveawayEntries(Base):
    __tablename__ = "giveaway_entries"
    entry_id = Column(Integer, primary_key=True)

    customer_id = Column(Integer, ForeignKey("customer.customer"))
    customer = relationship("Customer")

    giveaway_id = Column(Integer, ForeignKey("giveaways.giveaway_id"))
    customer = relationship("Customer")

    def get_entry_customer(self)-> Customer:
        return self.customer

    def get_entry_customer_name(self):
        return self.customer.discord_tag


class RaffleTicket(Base):
    __tablename__ = "raffle_ticket"
    ticket_number = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customer.customer"))
    customer = relationship("Customer")

    def get_ticket_owner_name(self):
        return self.customer.discord_tag
