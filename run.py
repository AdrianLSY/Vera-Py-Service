import json
from websocket import create_connection
from models import Event

def main():
    # Add status parameter as a query parameter in the URL
    ws = create_connection(
        "ws://localhost:4000/backend/websocket?status=ok",
        header=["Sec-WebSocket-Protocol: websocket"]  # Use standard websocket protocol
    )

    # Join the channel
    join_message = {
      "topic": "backend/service/3",
        "event": "phx_join",
        "payload": {},
        "ref": "1"
    }

    ws.send(json.dumps(join_message))
    print("Sent join message to channel service_api:1")

    # A simple loop to receive messages
    try:
        while True:
            message = ws.recv()
            print(message)
            message = json.loads(message)
            try:
                event = Event(**message)
                print(event.model_dump_json(indent=4))
            except Exception as e:
                print(e)
    except KeyboardInterrupt:
        ws.close()
        print("Connection closed.")

if __name__ == "__main__":
    main()
