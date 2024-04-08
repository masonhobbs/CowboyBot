from db.tables.base_db_class import BaseDbClass
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
class RollLogs(BaseDbClass):
    __tablename__ = "RollLog"

    Id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    UserId: Mapped[int]
    RollDate: Mapped[str]
    WasLucky: Mapped[bool]
    