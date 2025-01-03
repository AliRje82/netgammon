import socket


class BGPClient:
    def __init__(self, connect_to, host, port, timeout=0.001):
        self.connect_to = connect_to
        self.host = host
        self.port = port
        self.timeout = timeout
        self._socket = None

    @property
    def closed(self):
        return self._socket is None

    def connect(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if self.connect_to is None:
            # Listener mode
            self._socket.bind((self.host, self.port))
            self._socket.listen(1)
            print(f"Peer on {self.host}:{self.port}, waiting for a connection...")
            
            while True:
                try:
                    # Accept a connection, this call will block
                    connection, address = self._socket.accept()
                    print(f"Connected to {address}")
                    self._socket = connection  # Update the main socket to the accepted connection
                    break
                except socket.timeout:
                    # Timeout set, waiting for a connection
                    print("No connection yet, retrying...")
                    continue
                except Exception as e:
                    print(f"Error accepting connection: {e}")
                    break
        else:
            # Connector mode
            self._socket.settimeout(self.timeout)
            while True:
                try:
                    self._socket.connect((self.connect_to[0], self.connect_to[1]))
                    print(f"Connected to {self.connect_to[0]}:{self.connect_to[1]}")
                    break
                except socket.timeout:
                    print("Connection attempt timed out, retrying...")
                except BlockingIOError:
                    print("Still trying to connect...")
                    continue
                except Exception as e:
                    print(f"Error connecting to peer: {e}")
                    break
    

    def close(self):
        self._socket.close()
        self._socket = None

    def receive(self):
        message = self._socket.recv(10)
        message = message.decode('utf-8')
        print(message)
        formed_message = {'command': message[:(len(message.split()[0]))]}
        if message.startswith('DIES') or message.startswith('MOVE'):
            formed_message['args'] = tuple(int(i) for i in message[4:].split()[:2])
        elif message.startswith('COLOR'):
            formed_message['arg'] = message[5:].strip()
        return formed_message

    def send_dies(self, die1, die2):
        message = f'DIES {die1} {die2}'.ljust(10, ' ')
        self._socket.send(message.encode('utf-8'))

    def send_move(self, from_point, to_point):
        message = f'MOVE {from_point} {to_point}'.ljust(10, ' ')
        self._socket.send(message.encode('utf-8'))

    def send_end_move(self):
        message = 'ENDMOVE'.ljust(10, ' ')
        self._socket.send(message.encode('utf-8'))

    def send_quit(self):
        message = 'QUIT'.ljust(10, ' ')
        self._socket.send(message.encode('utf-8'))
