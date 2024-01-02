from db.tables.base_db_class import BaseDbClass
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
class RollStreakRecord(BaseDbClass):
    __tablename__ = "RollStreakRecord"

    Id: Mapped[int] = mapped_column(primary_key=True)
    HighestLuckyStreak: Mapped[int]
    HighestUnluckyStreak: Mapped[int]
