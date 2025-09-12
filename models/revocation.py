from core.database import base
from sqlalchemy import Column, DateTime, Index, func
from sqlalchemy.dialects.postgresql import UUID

class Revocation(base):
    """
    Model for storing revoked JWT tokens.
    
    This model tracks JWT tokens that have been revoked and should no longer
    be considered valid. The jti (JWT ID) field stores the UUID4 identifier
    from the JWT token.
    
    Attributes:
        jti (str): The JWT ID (UUID4) that was revoked.
        created_at (datetime): When the revocation was recorded.
    """
    __tablename__ = "revocations"

    jti = Column(UUID(as_uuid = True), primary_key = True, nullable = False)
    created_at = Column(DateTime(timezone = True), server_default = func.now(), nullable = False)

