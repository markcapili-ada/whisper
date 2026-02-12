from socketio import Client


sio = Client()


@sio.event
def connect():
    print("Connected to the server!")


@sio.event
def disconnect():
    print("Disconnected from the server.")


@sio.event
def signal(data):
    print(f"Received signal from server: {data}")
    if data["signal"] == "start_function":
        print("Starting function...")
        # Add your function logic here
    elif data["signal"] == "end_function":
        print("Ending function...")
        # Add your cleanup logic here


if __name__ == "__main__":
    try:
        url = "http://localhost:5432"
        sio.connect(url, namespaces=["/whisper"])
        sio.wait()  # Keep the client running to listen for signals
    except KeyboardInterrupt:
        print("Exiting client...")
        sio.disconnect()
