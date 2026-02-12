import signal
import time

import eventlet
from eventlet import wsgi
from socketio import Server, WSGIApp


# Initialize a Socket.IO server
sio = Server(async_mode="eventlet")


# Define the /whisper namespace
@sio.on("connect", namespace="/whisper")
def connect(sid, environ):
    print(f"Client {sid} connected to /whisper namespace")

    # Send an acknowledgment message to the client
    data = {"message": "Hello, client! This is a message from the server."}
    sio.send(data, to=sid, namespace="/whisper")
    print(f"Sent message to client {sid}: {data}")


@sio.on("disconnect", namespace="/whisper")
def disconnect(sid):
    print(f"Client {sid} disconnected from /whisper namespace")


@sio.on("message", namespace="/whisper")
def handle_message(sid, data):
    print(f"Received message from client {sid}: {data}")

    # Respond to the client with a custom event
    response_data = {"response": "Server received your message!"}
    sio.emit("my_response", response_data, to=sid, namespace="/whisper")


# Function to send periodic signals to the client
def send_signals():
    while True:
        time.sleep(2)  # Send a signal every 5 seconds
        signal_data = {"signal": "start_function 11"}
        print(f"Broadcasting signal to all clients: {signal_data}")
        sio.emit("start_live", signal_data, namespace="/whisper")

        time.sleep(2)  # Wait before sending the next signal
        signal_data = {"signal": "end_function 22"}
        print(f"Broadcasting signal to all clients: {signal_data}")
        sio.emit("end_live", signal_data, namespace="/whisper")


# Set up signal handling for graceful termination
def graceful_shutdown(signum, frame):
    print(f"Received signal {signum}, shutting down...")
    eventlet.kill()


# Wrap the server in a WSGI application
app = WSGIApp(sio)

if __name__ == "__main__":
    host = "0.0.0.0"
    port = 5432

    print(f"Starting server on {host}:{port}")

    # Start the signal loop in a separate thread
    eventlet.spawn(send_signals)

    # Set up signal handling for graceful shutdown
    signal.signal(signal.SIGTERM, graceful_shutdown)
    signal.signal(signal.SIGINT, graceful_shutdown)

    # Start the server
    wsgi.server(eventlet.listen((host, port)), app)
