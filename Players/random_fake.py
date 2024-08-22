from Players.player import Player
import random

class RandomFake(Player):
    def __init__(self, name):
        super().__init__(name)
    
    def check_play_logic(self, event):
        if (event.player_turn == self):
            if (random.uniform(0, 1) > .6):
                return self.fake_card()
            else:
                return self.play_card()