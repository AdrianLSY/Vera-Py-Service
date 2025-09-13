from core.database import base
from sqlalchemy import Column, DateTime, Index, func, text
from sqlalchemy.dialects.postgresql import UUID
from typing import Optional

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
        nullable = False,
        index = True
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

    @classmethod
    def cleanup_expired_revocations(cls, db_session) -> int:
        """
        Remove expired revocation records from the database.
        
        This method deletes all revocation records where the expires_at timestamp
        is in the past, helping to keep the revocations table clean and performant.
        For high-volume systems, consider scheduling this as a background task.
        
        Parameters:
            db_session: Database session to execute the cleanup.
            
        Returns:
            int: Number of records deleted.
            
        Raises:
            Exception: If database operation fails.
        """
        result = db_session.execute(
            text("DELETE FROM revocations WHERE expires_at < NOW()")
        )
        return result.rowcount

    @classmethod
    def get_expired_count(cls, db_session) -> int:
        """
        Get the count of expired revocation records.
        
        This method counts how many revocation records have expired and could
        be cleaned up, useful for monitoring and scheduling cleanup operations.
        
        Parameters:
            db_session: Database session to execute the query.
            
        Returns:
            int: Number of expired revocation records.
            
        Raises:
            Exception: If database operation fails.
        """
        result = db_session.execute(
            text("SELECT COUNT(*) FROM revocations WHERE expires_at < NOW()")
        )
        return result.scalar()

