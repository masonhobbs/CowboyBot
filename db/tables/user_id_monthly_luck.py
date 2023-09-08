from db.tables.base_db_class import BaseDbClass
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
class UserIdMonthlyLuck(BaseDbClass):
    __tablename__ = "UserIdMonthlyLuck"

    UserId: Mapped[int] = mapped_column(primary_key=True)
    Username: Mapped[str]
    CurrentMonthNumber: Mapped[int]
    LuckyCount: Mapped[int] 
    UnluckyCount: Mapped[int]
    LastRoll: Mapped[str]
    CurrentLuckyStreak: Mapped[int]
    CurrentUnluckyStreak: Mapped[int]