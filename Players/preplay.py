from Players.player import Player

class Preplay(Player):
    def __init__(self, name):
        super().__init__(name)

    def check_slap_logic(self, event):
        default = super().check_slap_logic(event)
        if (default != None):
            return default
        if (len(self.memory) > 0):
            if (event.player_turn in event.movements and self.memory[-1].rank in ["J"]):
                return self.preslap()
    
    def check_play_logic(self, event):
        default = super().check_play_logic(event)
        if (default != None):
            return default
        if (self.player_before in event.movements and self.royal_sequence == False):
            return self.play_card()