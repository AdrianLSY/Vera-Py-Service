from sqlalchemy import Column, DateTime, Index, Integer, String, func

from core.database import base


class User(base):
    """
    Model for application users.

    This model stores information about registered users, including their
    login credentials, contact details, and lifecycle timestamps. It enforces
    uniqueness constraints on username, email, and phone number to ensure
    account integrity. At least one of username, email, or phone_number must
    be provided. Soft deletion is supported via the deleted_at field.

    Attributes:
        id (int): Primary key, auto-incrementing user identifier.
        username (str | None): Optional unique username for login and identification.
        name (str): Full display name of the user.
        email (str | None): Optional unique email address of the user.
        phone_number (str | None): Optional unique phone number of the user.
        password_digest (str): Hashed user password.
        created_at (datetime): Timestamp when the user record was created.
        updated_at (datetime): Timestamp of the last update.
        deleted_at (datetime | None): Nullable timestamp for soft deletion.

    Indexes:
        - username, email, phone_number (for uniqueness and fast lookup)
        - deleted_at (for filtering out active vs. deleted users)
        - created_at (for sorting and auditing)
        - updated_at (for sorting and auditing)
    """

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key = True,
        autoincrement = True,
        index = True
    )
    username = Column(
        String,
        nullable = True,
        unique = True,
        index = True
    )
    name = Column(
        String,
        nullable = False
    )
    email = Column(
        String,
        nullable = True,
        unique = True,
        index = True
    )
    phone_number = Column(
        String,
        nullable = True
    )
    password_digest = Column(
        String,
        nullable = False
    )
    created_at = Column(
        DateTime(timezone = True),
        server_default = func.now(),
        nullable = False,
        index = True
    )
    updated_at = Column(
        DateTime(timezone = True),
        server_default = func.now(),
        onupdate = func.now(),
        nullable = False,
        index = True
    )
    deleted_at = Column(
        DateTime(timezone = True),
        nullable = True,
        index = True
    )

    __table_args__ = (
        Index(
            "idx_users_username",
            "username"
        ),
        Index(
            "idx_users_email",
            "email"
        ),
        Index(
            "idx_users_deleted_at",
            "deleted_at"
        ),
    )
