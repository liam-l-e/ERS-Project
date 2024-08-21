from GameFiles.ers_game import Game
from Players.player import Player
from Players.never_slap import NeverSlap

def main():
    players = [Player("Jonathan"), Player("Dylan"), Player("Liam")]

    game = Game(players)
    game.play_game()

if __name__ == "__main__":
    main()
