from db.tables.base_db_class import BaseDbClass
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
class CowboyReacts(BaseDbClass):
    __tablename__ = "CowboyReacts"

    Id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    TriggerWord: Mapped[str]