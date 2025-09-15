from logging.config import fileConfig
import os
import sys
import importlib
from os import getenv
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy import pool

from alembic import context

from core.database import base

def import_all_models() -> None:
    """
    Automatically discover and import all model classes from the models/ directory.

    This function scans the models directory for Python files and imports them,
    ensuring all SQLAlchemy models are registered with the metadata for Alembic.
    """
    models_dir = Path(__file__).parent.parent / "models"

    if not models_dir.exists():
        return

    # Get all Python files in the models directory
    for model_file in models_dir.glob("*.py"):
        # Skip __init__.py and __pycache__ files
        if model_file.name.startswith("__"):
            continue

        # Convert file path to module name
        module_name = f"models.{model_file.stem}"

        try:
            # Import the module
            importlib.import_module(module_name)
        except ImportError as exc:
            # Log the error but don't fail - some models might have dependencies
            print(f"Warning: Could not import {module_name}: {exc}")

def get_database_url() -> str:
    """
    Get the database URL from alembic config or environment variables.

    First tries to use the sqlalchemy.url from the alembic configuration.
    If not available, falls back to constructing URL from environment variables.

    Returns:
        str: The database URL for PostgreSQL connection.

    Raises:
        ValueError: If required environment variables are missing.
    """
    # First, try to get URL from alembic config
    config_url = context.config.get_main_option("sqlalchemy.url")
    if config_url:
        return config_url

    # Fall back to environment variables
    host = getenv("POSTGRES_HOST")
    port = getenv("POSTGRES_PORT")
    username = getenv("POSTGRES_USER")
    password = getenv("POSTGRES_PASSWORD")

    if not all([host, port, username, password]):
        raise ValueError("Missing required database environment variables")

    # Determine database based on environment
    environment = getenv("ENVIRONMENT", "test")

    if environment == "development":
        database = getenv("POSTGRES_DB_DEVELOPMENT")
    elif environment == "production":
        database = getenv("POSTGRES_DB_PRODUCTION")
    else:  # test environment
        database = getenv("POSTGRES_DB_TEST")

    if database is None:
        raise ValueError(f"Database name not configured for environment: {environment}")

    return f"postgresql://{username}:{password}@{host}:{port}/{database}"


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = get_database_url()
    context.configure(
        url = url,
        target_metadata = target_metadata,
        literal_binds = True,
        dialect_opts = {"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    database_url = get_database_url()
    connectable = create_engine(
        database_url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection = connection,
            target_metadata = target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

import_all_models()
target_metadata = base.metadata

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
