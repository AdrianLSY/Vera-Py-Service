from core.database import base
from sqlalchemy import Column, Integer, String, DateTime, Index, func

class User(base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True, autoincrement = True)
    username = Column(String, nullable = False, unique = True, index = True)
    password_digest = Column(String, nullable = False)
    created_at = Column(DateTime(timezone = True), server_default = func.now(), nullable = False)
    updated_at = Column(DateTime(timezone = True), server_default = func.now(), onupdate = func.now(), nullable = False)
    deleted_at = Column(DateTime(timezone = True), nullable = True, index = True)

    __table_args__ = (
        Index("idx_users_username", "username"),
        Index("idx_users_deleted_at", "deleted_at"),
    )
