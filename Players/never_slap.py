from Players.player import Player

class NeverSlap(Player):
    def __init__(self, name):
        super().__init__(name)
    
    def check_slap_logic(self, event):
        return None