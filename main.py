from backgammon import Backgammon
from backgammon_client import BackgammonGameClient
import sys


host = '127.0.0.1'
port = int(sys.argv[1])

connect_to = None
if len(sys.argv) > 3:
    connect_to = (sys.argv[2], int(sys.argv[3]))

game = Backgammon()
game_client = BackgammonGameClient(game, connect_to, host, port)
game_client.run()
