from db.tables.base_db_class import BaseDbClass
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
class UserIdLuck(BaseDbClass):
    __tablename__ = "UserIdLuck"

    UserId: Mapped[int] = mapped_column(primary_key=True)
    Username: Mapped[str]
    LuckyCount: Mapped[int] 
    UnluckyCount: Mapped[int]
    LastRoll: Mapped[str]
    CurrentLuckyStreak: Mapped[int]
    CurrentUnluckyStreak: Mapped[int]
