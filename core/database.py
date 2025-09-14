from os import getenv
from contextlib import contextmanager
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
    
    def __new__(cls) -> 'Database':
        """
        Create or return the singleton instance.
        
        Returns:
            Database: The singleton instance.
        """
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance
    
    def initialize(
        self,
        host: str,
        port: str,
        username: str,
        password: str,
        database: str
    ) -> None:
        """
        Initialize the database connection using provided parameters.
        
        Parameters:
            host (str): Database host.
            port (str): Database port.
            username (str): Database username.
            password (str): Database password.
            database (str): Database name.
            
        Raises:
            ValueError: If required parameters are missing or invalid.
        """
        if not all([host, port, username, password, database]):
            raise ValueError("All database parameters must be provided")
        
        database_url = f"postgresql://{username}:{password}@{host}:{port}/{database}"
        self.__engine = create_engine(database_url)
        self.__session_factory = sessionmaker(bind = self.__engine)
    
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
        
        # Get the database URL from the engine
        database_url = str(self.__engine.url)
        
        # Create alembic config
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        
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
        
        # Get the database URL from the engine
        database_url = str(self.__engine.url)
        
        # Create alembic config
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        
        try:
            # Rollback all migrations to base state
            command.downgrade(alembic_cfg, "base")
        except Exception as exc:
            raise RuntimeError(f"Database teardown failed: {exc}") from exc

base = declarative_base()
database = Database()
