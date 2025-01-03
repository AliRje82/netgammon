from backgammon import Backgammon
from backgammon_client import BackgammonGameClient
import sys
import pygame



port = int(sys.argv[1])

game = Backgammon()
game_client = BackgammonGameClient(game,port)
game_client.run()
