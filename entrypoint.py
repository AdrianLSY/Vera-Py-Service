from asyncio import run
from os import getenv

from core.database import database
from core.plugboard_client import PlugboardClient

if __name__ == "__main__":
    websocket_url = getenv("WEBSOCKET_URL")
    token = getenv("TOKEN")

    if websocket_url is None or token is None:
        raise ValueError("WEBSOCKET_URL and TOKEN environment variables must be set")

    # Determine database based on environment
    environment = getenv("ENVIRONMENT", "test")

    if environment == "development":
        db = getenv("POSTGRES_DB_DEVELOPMENT")
    elif environment == "production":
        db = getenv("POSTGRES_DB_PRODUCTION")
    else:  # test environment
        db = getenv("POSTGRES_DB_TEST")

    if db is None:
        raise ValueError(f"Database name not configured for environment: {environment}")

    database.initialize()
    database.migrate()

    run(
        PlugboardClient().connect(
            websocket_url = websocket_url,
            token = token
        )
    )
