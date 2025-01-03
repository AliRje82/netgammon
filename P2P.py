import socket
import threading
import random

host = '127.0.0.1'
connection = None


def handle_message(message):
    global connection
    if connection:
        connection.send(message.encode())

def receive_message():
    global connection
    while True:
        try:
            data = connection.recv(1024)
            if not data:
                break
            message = data.decode()
            print(f"Opponent send {message}")
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

def send_message():
    while True:
        message = input("You: ")
        print(f"You send {message}")
        handle_message(message)

def peer_connection():
    global connection
    mode = input("host or peer: ").strip().lower()
    if mode == "host":
        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_socket.bind((host, 1383))
        peer_socket.listen(1)
        port = peer_socket.getsockname()[1]
        print(f"Peer on {host}:{port}, waiting for a connection...")
        connection, address = peer_socket.accept()
        print(f"Connected to {address}")
    else:
        port = int(input("Enter the host port: ").strip())
        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_socket.connect((host, port))
        connection = peer_socket
        print(f"Connected to {host}:{port}")
  
    threading.Thread(target=receive_message, daemon=True).start()
    send_message()

if __name__ == "__main__":
    peer_connection()
