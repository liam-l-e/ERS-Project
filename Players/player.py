import random
from GameFiles.game_event import GameEvent
from GameFiles.game_action import GameAction

## Player representation with name,hand,and play first card
class Player:
    def __init__(self,  name):
        self.name = name
        self.hand = []
        self.reaction_time = random.uniform(0.25,0.3)
        self.queued_action = None
        self.memory = []
        self.player_before = None

    # Reaction to game event
    def react_to_event(self, event):
        # Clear queue action if there was a new pile
        if event.new_pile:
            reaction = self.new_pile()
            if (reaction): return reaction
        # Store event into memory
        self.event_memory(event)
        # Clear queued action from previous event
        reaction = self.clear_action_queue()
        if (reaction): return reaction
        # Check if you are the pile winner
        if (event.pile_winner == self):
            return self.slap()
        # Check slapping logic
        reaction = self.check_slap_logic(event)
        if (reaction): return reaction
        # Check playing logic
        reaction = self.check_play_logic(event)
        if (reaction): return reaction
        # Else just wait
        return self.wait()
    
    # Default event memory
    def event_memory(self, event : GameEvent):
        for card in event.cards:
            self.memory.append(card)
        for i in range(len(event.player_rotation)):
            if (event.player_rotation[i] == self):
                self.player_before = event.player_rotation[i-1]
        if (event.new_pile):
            self.memory = []

    def new_pile(self):
        self.queued_action = None
        if (len(self.hand) <= 0):
            return self.leave_game()
        return None

    # Default slap logic
    def check_slap_logic(self, event):
        if len(self.memory) >= 2:
            # Check for double
            if self.memory[-1].rank == self.memory[-2].rank:
                return self.slap()
            
            # Check for marriage
            if (self.memory[-1].rank in ['K', 'Q'] and self.memory[-2].rank in ['K', 'Q']) and (self.memory[-1].rank != self.memory[-2].rank):
                return self.slap()

            if len(self.memory) >= 3:
                # Check for sandwich
                if self.memory[-1].rank == self.memory[-3].rank:
                    return self.slap()
                
            if len(self.memory) >= 3:
                # Check for divorce
                if self.memory[-1].rank in['K','Q'] and self.memory[-3].rank in ['K','Q']:
                    return self.slap()
        return None
    
    def get_top_card(self):
        if (len(self.hand) <= 0):
            return None
        return self.hand.pop(0)

    # Default play logic
    def check_play_logic(self, event : GameEvent):
        if (event.player_turn == self):
            return self.play_card()

    # Automatically do action queue from previous event
    def clear_action_queue(self):
        if (callable(self.queued_action)):
            return self.queued_action()
        if self.queued_action:
            temp_action = self.queued_action
            self.queued_action = None
            return temp_action
    
    # Start up playing card action starts movement and queues card
    def play_card(self):
        # Queue negative time for the card so its always first
        self.queued_action = GameAction("Card", self, -random.uniform(0, 1))
        return GameAction("Movement", self, self.get_reaction_time())
    
    def leave_game(self):
        return GameAction("Leave", self, -1)
        
    # Start up faking card action starts movement and queues fake
    def fake_card(self):
        # Queue negative time for the fake so its always first
        self.queued_action = GameAction("Fake", self, -random.uniform(0, 1))
        return GameAction("Movement", self, self.get_reaction_time())
        
    # Slaps the pile on reaction
    def slap(self):
        return GameAction("Slap", self, self.get_reaction_time())

    # Will wait this turn and slap fast on next event
    def preslap(self):
        self.queued_action = GameAction("Slap", self, self.get_prediction_time())
        return self.wait()
    
    # Queues both playing card and slap right after
    def play_and_preslap(self):
        def play_and_slap():
            self.queued_action = GameAction("Slap", self, self.get_prediction_time())
            return GameAction("Card", self, -random.uniform(0, 1))
        self.queued_action = play_and_slap
        return GameAction("Movement", self, self.get_reaction_time())
    
    # Wait for next event
    def wait(self):
        return GameAction("Wait", self, self.get_reaction_time())
    
    # Gets normal reaction time
    def get_reaction_time(self):
        return self.reaction_time + random.uniform(0, .5)
    
    # Gets predicted reaction time
    def get_prediction_time(self):
        return self.get_reaction_time() / 4