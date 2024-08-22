from GameFiles.ers_game import Game
from Players.player import Player
from Players.never_slap import NeverSlap
from Players.random_fake import RandomFake
from Players.preplay import Preplay
from random import shuffle

def new_game():
    players = [RandomFake("Jonathan"), Preplay("Dylan"), Player("Liam"), Player("Kuli")]
    # Give random order to player rotation
    shuffle(players)

    # Play game without printing any messages
    game = Game(players, print_messages=False)
    return game.play_game().name

def main():
    player_wins = {
        "Jonathan": 0, 
        "Dylan": 0, 
        "Liam": 0, 
        "Kuli": 0
    }
    for _ in range(100):
        winner_name = new_game()
        player_wins[winner_name] += 1
    
    for player in player_wins:
        print(f"{player} won {player_wins[player]} games")

if __name__ == "__main__":
    main()
