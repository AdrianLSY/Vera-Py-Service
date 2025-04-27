from os import getenv
from asyncio import run
from core.plugboard_client import PlugboardClient

if __name__ == '__main__':
    websocket_url = getenv("WEBSOCKET_URL")
    token = getenv("TOKEN")
    
    if websocket_url is None or token is None:
        raise ValueError("WEBSOCKET_URL and TOKEN environment variables must be set")
    
    run(
        PlugboardClient().connect(
            websocket_url=websocket_url,
            token=token
        )
    )