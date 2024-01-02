from db.tables.base_db_class import BaseDbClass
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
class FeatureRequests(BaseDbClass):
    __tablename__ = "FeatureRequestsV3"

    Id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    Request: Mapped[str]
    User: Mapped[str]
