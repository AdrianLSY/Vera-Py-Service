from os import getenv
from asyncio import run
from core.client import PlugboardClient

if __name__ == '__main__':
    client = PlugboardClient()
    run(client.connect(service_id = getenv("SERVICE_ID")))
