from os import getenv
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

from sqlalchemy.orm import declarative_base


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
    
    def initialize(self) -> None:
        """
        Initialize the database connection using environment variables.
        
        Environment Variables:
            DB_HOST (str): Database host. Defaults to 'localhost'.
            DB_PORT (str): Database port. Defaults to '5432'.
            DB_USERNAME (str): Database username. Defaults to 'postgres'.
            DB_PASSWORD (str): Database password. Defaults to 'postgres'.
            DB_NAME (str): Database name. Defaults to 'postgres'.
            
        Raises:
            ValueError: If required environment variables are missing or invalid.
        """
        host = getenv("DB_HOST", "localhost")
        port_str = getenv("DB_PORT", "5432")
        username = getenv("DB_USERNAME", "postgres")
        password = getenv("DB_PASSWORD", "postgres")
        database = getenv("DB_NAME", "postgres")
        
        try:
            port = int(port_str)
        except ValueError:
            raise ValueError(f"Invalid DB_PORT value: {port_str}. Must be a valid integer.")
        
        database_url = f"postgresql://{username}:{password}@{host}:{port}/{database}"
        self.__engine = create_engine(database_url)
        self.__session_factory = sessionmaker(bind = self.__engine)
    
    def session(self) -> Generator[Session, None, None]:
        """
        Get a database session.
        
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
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    @contextmanager
    def transaction(self) -> Generator[Session, None, None]:
        """
        Get a database session with transaction management.
        
        Yields:
            Session: A SQLAlchemy session instance.
        """
        yield from self.session()


base = declarative_base()
database = Database()
