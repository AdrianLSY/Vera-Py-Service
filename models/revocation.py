from core.database import base
from sqlalchemy import Column, DateTime, Index, func
from sqlalchemy.dialects.postgresql import UUID

class Revocation(base):
    """
    Model for storing revoked JWT tokens.
    
    This model tracks JWT tokens that have been revoked and should no longer
    be considered valid. The jti (JWT ID) field stores the UUID4 identifier
    from the JWT token. The expires_at field stores when the token naturally
    expires, enabling cleanup of old revocation records.
    
    For future scaling, consider implementing a bloom filter to improve lookup performance.
    
    Attributes:
        jti (str): The JWT ID (UUID4) that was revoked.
        created_at (datetime): When the revocation was recorded.
        expires_at (datetime): When the JWT token naturally expires.
    
    Indexes:
        - jti (for unique revocation)
        - created_at (for sorting and auditing)
        - expires_at (for cleanup)
    """
    __tablename__ = "revocations"

    jti = Column(
        UUID(as_uuid = True),
        primary_key = True,
        nullable = False
    )
    created_at = Column(
        DateTime(timezone = True),
        server_default = func.now(),
        nullable = False,
        index = True
    )
    expires_at = Column(
        DateTime(timezone = True),
        nullable = True,
        index = True
    )

    __table_args__ = (
        Index(
            "idx_revocations_expires_at",
            "expires_at"
        ),
        Index(
            "idx_revocations_created_at",
            "created_at"
        ),
    )
