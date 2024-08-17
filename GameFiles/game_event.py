class GameEvent:
    def __init__(self, player_turn):
        self.player_turn = player_turn
        self.cards = []
        self.movements = []
        self.new_pile = None
        self.start_to_play = []
        self.burned = []
        self.pile_winner = None