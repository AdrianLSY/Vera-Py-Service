import sys

def migration():
    from json import dump, load
    from os.path import abspath, dirname, join

    # Get the directory of the current script
    current_dir = dirname(abspath(__file__))
    schema_path = join(current_dir, 'schema', 'schema.json')

    with open(schema_path, 'r') as file:
        data = load(file)

    with open(schema_path, 'w') as file:
        dump(data, file, indent = 4)
        file.write('\n')

def client():
    from os import getenv
    from asyncio import run
    from core.client import PlugboardClient

    run(
        PlugboardClient().connect(
            service_id = getenv("SERVICE_ID")
        )
    )

if __name__ == '__main__':
    if sys.argv[1] == 'client':
        client()
    if sys.argv[1] == 'migration':
        migration()
    raise Exception(f"{sys.argv[1]} is not a valid command. Please use 'client' or 'migration'.")
