from os import getenv
from asyncio import run
from core.plugboard_client import PlugboardClient

if __name__ == '__main__':
    run(
        PlugboardClient().connect(
            websocket_url = getenv("WEBSOCKET_URL"),
            service_id = getenv("SERVICE_ID"),
            token = getenv("TOKEN")
        )
    )
