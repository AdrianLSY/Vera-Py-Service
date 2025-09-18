from sqlalchemy import Column, DateTime, Integer, func

from core.database import base


class Bar(base):
    __tablename__ = "bar"

    bar: int = Column(
        Integer,
        primary_key = True,
    )
    created_at = Column(
        DateTime(timezone = True),
        server_default = func.now(),
        nullable = False,
    )
    updated_at = Column(
        DateTime(timezone = True),
        onupdate = func.now(),
        server_default = func.now(),
        nullable = False,
    )
