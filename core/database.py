from contextlib import contextmanager
from os import getenv
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm import declarative_base

from alembic.config import Config
from alembic import command


class Database:
    """
    Singleton class for managing database sessions.

    This class ensures only one database connection is created
    and reused throughout the application lifecycle.
    """
    __instance: Optional['Database'] = None
    __engine: Optional[Engine] = None
    __session_factory: Optional[sessionmaker] = None
    __host: Optional[str] = None
    __port: Optional[str] = None
    __username: Optional[str] = None
    __password: Optional[str] = None
    __environment: Optional[str] = None
    __database: Optional[str] = None

    def __new__(cls) -> 'Database':
        """
        Create or return the singleton instance.

        Returns:
            Database: The singleton instance.
        """
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def initialize(self) -> None:
        """
        Initialize the database connection using environment variables.

        Reads database configuration from environment variables:
        - POSTGRES_HOST: Database host (default: localhost)
        - POSTGRES_PORT: Database port (default: 5432)
        - POSTGRES_USER: Database username (default: auth)
        - POSTGRES_PASSWORD: Database password (default: auth)
        - ENVIRONMENT: Environment name (development/test/production)
        - POSTGRES_DB_DEVELOPMENT: Development database name
        - POSTGRES_DB_TEST: Test database name
        - POSTGRES_DB_PRODUCTION: Production database name

        Raises:
            ValueError: If required environment variables are missing or invalid.
        """
        self.__host = getenv("POSTGRES_HOST")
        self.__port = getenv("POSTGRES_PORT")
        self.__username = getenv("POSTGRES_USER")
        self.__password = getenv("POSTGRES_PASSWORD")
        self.__environment = getenv("ENVIRONMENT")

        # Select database based on environment
        if self.__environment == "test":
            self.__database = getenv("POSTGRES_DB_TEST")
        elif self.__environment == "production":
            self.__database = getenv("POSTGRES_DB_PRODUCTION")
        else:  # development
            self.__database = getenv("POSTGRES_DB_DEVELOPMENT")

        if not self.__database:
            raise ValueError(f"Database name not configured for environment: {self.__environment}")

        database_url = f"postgresql://{self.__username}:{self.__password}@{self.__host}:{self.__port}/{self.__database}"
        self.__engine = create_engine(database_url)
        self.__session_factory = sessionmaker(bind = self.__engine)

    def deinitialize(self) -> None:
        """
        Deinitialize the database singleton by resetting all instance variables.

        This method closes any existing connections, resets the singleton instance,
        and allows for reinitialization with different configuration. Useful for
        testing scenarios or when database configuration needs to be changed.
        """
        # Close any existing sessions if they exist
        if self.__session_factory is not None:
            self.__session_factory = None

        # Dispose of the engine if it exists
        if self.__engine is not None:
            self.__engine.dispose()
            self.__engine = None

        # Reset configuration properties
        self.__host = None
        self.__port = None
        self.__username = None
        self.__password = None
        self.__environment = None
        self.__database = None

        # Reset the singleton instance
        Database.__instance = None

    @property
    def engine(self) -> Optional[Engine]:
        """
        Get the database engine instance.

        Returns:
            Optional[Engine]: The SQLAlchemy engine instance, or None if not initialized.
        """
        return self.__engine

    @property
    def session_factory(self) -> Optional[sessionmaker]:
        """
        Get the session factory instance.

        Returns:
            Optional[sessionmaker]: The SQLAlchemy session factory, or None if not initialized.
        """
        return self.__session_factory

    @property
    def host(self) -> Optional[str]:
        """
        Get the database host.

        Returns:
            Optional[str]: The database host, or None if not initialized.
        """
        return self.__host

    @property
    def port(self) -> Optional[str]:
        """
        Get the database port.

        Returns:
            Optional[str]: The database port, or None if not initialized.
        """
        return self.__port

    @property
    def username(self) -> Optional[str]:
        """
        Get the database username.

        Returns:
            Optional[str]: The database username, or None if not initialized.
        """
        return self.__username

    @property
    def password(self) -> Optional[str]:
        """
        Get the database password.

        Returns:
            Optional[str]: The database password, or None if not initialized.
        """
        return self.__password

    @property
    def environment(self) -> Optional[str]:
        """
        Get the current environment.

        Returns:
            Optional[str]: The environment name, or None if not initialized.
        """
        return self.__environment

    @property
    def database_name(self) -> Optional[str]:
        """
        Get the database name.

        Returns:
            Optional[str]: The database name, or None if not initialized.
        """
        return self.__database

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """
        Get a raw database session without auto-commit/rollback.

        Yields:
            Session: A SQLAlchemy session instance.

        Raises:
            RuntimeError: If database is not initialized.
        """
        if self.__session_factory is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")

        session = self.__session_factory()
        try:
            yield session
        finally:
            session.close()

    @contextmanager
    def transaction(self) -> Generator[Session, None, None]:
        """
        Get a database session with automatic transaction management.

        Automatically commits on success and rolls back on exception.

        Yields:
            Session: A SQLAlchemy session instance.
        """
        with self.session() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    def migrate(self) -> None:
        """
        Run database migrations using Alembic.

        Raises:
            RuntimeError: If database is not initialized or migration fails.
        """
        if self.__engine is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")

        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option(
            "sqlalchemy.url",
            f"postgresql://{self.__username}:{self.__password}@{self.__host}:{self.__port}/{self.__database}"
        )

        try:
            # Run migrations to the latest version
            command.upgrade(alembic_cfg, "head")
        except Exception as exc:
            raise RuntimeError(f"Migration failed: {exc}") from exc

    def teardown(self) -> None:
        """
        Teardown the database by rolling back all migrations to base state.

        This effectively runs 'alembic downgrade base' to remove all
        database tables and data created by migrations.

        Raises:
            RuntimeError: If database is not initialized or teardown fails.
        """
        if self.__engine is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")

        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option(
            "sqlalchemy.url",
            f"postgresql://{self.__username}:{self.__password}@{self.__host}:{self.__port}/{self.__database}"
        )

        try:
            # Rollback all migrations to base state
            command.downgrade(alembic_cfg, "base")
        except Exception as exc:
            raise RuntimeError(f"Database teardown failed: {exc}") from exc

base = declarative_base()
database = Database()
