import random
import time
from queue import PriorityQueue

## Card representation with rank and suit
class Card:
    def __init__(self,rank,suit):
        self.rank=rank
        self.suit=suit

    def __str__(self):
        return f"{self.rank} of {self.suit}"

class GameAction: 
    def __init__(self, type, player, time):
        self.action_type = type
        self.player = player
        self.time = time

    def __lt__(self, other):
        # Less than: self < other
        if isinstance(other, GameAction):
            return self.time < other.time
        return NotImplemented

    def __le__(self, other):
        # Less than or equal to: self <= other
        if isinstance(other, GameAction):
            return self.time <= other.time
        return NotImplemented

    def __eq__(self, other):
        # Equal to: self == other
        if isinstance(other, GameAction):
            return self.time == other.time
        return NotImplemented

    def __ne__(self, other):
        # Not equal to: self != other
        if isinstance(other, GameAction):
            return self.time != other.time
        return NotImplemented

    def __gt__(self, other):
        # Greater than: self > other
        if isinstance(other, GameAction):
            return self.time > other.time
        return NotImplemented

    def __ge__(self, other):
        # Greater than or equal to: self >= other
        if isinstance(other, GameAction):
            return self.time >= other.time
        return NotImplemented
    
    def __str__(self) -> str:
        return f"GameAction: player {self.player.name}, action {self.action_type}, time {self.time}"

class GameEvent:
    def __init__(self, player_turn):
        self.player_turn = player_turn
        self.cards = []
        self.movements = []
        self.new_pile = None
        self.start_to_play = []
        self.burned = []
        self.pile_winner = None

## Player representation with name,hand,and play first card
class Player:
    def __init__(self,  name):
        self.name = name
        self.hand = []
        self.reaction_time = random.uniform(0.1,0.5)
        self.queued_action = None
        self.memory = []

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
        self.queued_action = Game("Slap", self, self.get_prediction_time())
        return self.wait()
    
    # Queues both playing card and slap right after
    def play_and_preslap(self):
        pass
    
    # Wait for next event
    def wait(self):
        return GameAction("Wait", self, self.get_reaction_time())
    
    # Gets normal reaction time
    def get_reaction_time(self):
        return self.reaction_time + random.uniform(.02, .1)
    
    # Gets predicted reaction time
    def get_prediction_time(self):
        return self.get_reaction_time() / 4


## Representation of game logic
class Game:
    def __init__(self,players):
        self.players: list[Player] = players
        self.pile: list[Card] = []
        self.burned: list[Card] = []
        self.current_player_index = 0
        self.played_royal = None
        self.cards_to_play = 0
        self.total_cards = 52
        self.pile_winner = None
        self.slapped = None
        self.game_event : GameEvent = None
        self.skip_players: set[Player] = set()

        #Deal the cards
        self.create_deck()

    ## Rank and suit creation
    def create_deck(self):
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        deck = [Card(rank,suit) for suit in suits for rank in ranks]
        random.shuffle(deck)

        cards_per_player = len(deck) // len(self.players)
        remainder = len(deck) % len(self.players)

        # deal
        for player in self.players:
            player.hand = [deck.pop() for _ in range(cards_per_player)]

        # Place remaining card(s) in the burned pile to start the game
        self.burned = [deck.pop() for _ in range(remainder)]

        self.log_card_count("After initial deal",1)
    
    # Increments player turn
    def next_player(self):
        if self.pile_winner:
            index = self.players.index(self.pile_winner)
            self.current_player_index = index
        else:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            while (self.players[self.current_player_index] in self.skip_players):
                self.current_player_index = (self.current_player_index + 1) % len(self.players)
    
    # Handle actions from players
    def handle_new_action(self, action: GameAction):
        match action.action_type:
            case "Movement":
                self.game_event.movements.append(action.player)
            case "Card":
                card = action.player.get_top_card()
                if (card == None):
                    self.temp_remove_player(action.player)
                else:
                    self.handle_new_card(action.player, card)
            case "Slap":
                self.handle_slap(action.player)
            case "Leave":
                self.full_remove_player(action.player)
            case _:
                pass

    def temp_remove_player(self, player):
        print(f"{player.name} ran out of cards")
        if self.played_royal:
            print(f"{self.played_royal.name} wins royal sequence!")
            self.pile_winner = self.played_royal
            self.game_event.pile_winner = self.played_royal
        else:
            self.skip_players.add(player)
            if (len(self.players) - len(self.skip_players) == 1):
                last_player = None
                for player in self.players:
                    if (player not in self.skip_players):
                        last_player = player
                        break
                last_player.hand.extend(self.burned)
                last_player.hand.extend(self.pile)
                print(f"{last_player.name} took the pile")
                self.game_event.new_pile = True
                self.reset_pile()
            self.next_player()

    def full_remove_player(self, player):
        print(f"Full remove {player.name} is out of the game")
        self.players.remove(player)
        self.current_player_index = self.players.index(self.game_event.player_turn)

    # Handle a players slap
    def handle_slap(self, player):
        print(f"{player.name} slapped the pile")
        # Handle when the miss slap and have to burn
        if not self.is_slappable(player):
            burned_card = player.get_top_card()
            if (burned_card == None):
                self.temp_remove_player(player)
                return
            print(f"{player.name} burned the {burned_card} because they slapped the pile")
            self.burned.append(burned_card)
            self.game_event.burned.append(burned_card)
            return
        # Handle when they slap first
        if not self.slapped:
            self.slapped = player
        # Handle when they slap after someone else
        else:
            pass

    # Handle player playing card
    def handle_new_card(self, player, card):
        print(f"{player.name} played the {card}")
        # Check if they played out of turn then they burn
        if self.players[self.current_player_index] != player:
            print(f"{player.name} burned the {card} because they were out of turn")
            self.burned.append(card)
            self.game_event.burned.append(card)
            return
        # Handle when they play in turn
        self.pile.append(card)
        self.game_event.cards.append(card)

        # Handle royal sequences
        self.handle_played_royal(player, card)
        # Increment turn
        if not self.played_royal:
            self.next_player()

    ## Slap logic (doubles, sandwiches, marriages)
    def is_slappable(self, player):
        if len(self.pile) >= 2:
            # Check for double
            if self.pile[-1].rank == self.pile[-2].rank:
                return "Double"
            
            # Check for marriage
            if (self.pile[-1].rank in ['K', 'Q'] and self.pile[-2].rank in ['K', 'Q']) and (self.pile[-1].rank != self.pile[-2].rank):
                return "Marriage"

            if len(self.pile) >= 3:
                # Check for sandwich
                if self.pile[-1].rank == self.pile[-3].rank:
                    return "Sandwich"
                
            if len(self.pile) >= 3:
                # Check for divorce
                if self.pile[-1].rank in['K','Q'] and self.pile[-3].rank in ['K','Q']:
                    return "Divorce"
                
        if (player == self.pile_winner):
            return "Royal Win"
                
        return False
    
    def get_cards_for_royal(self,rank):
        royal_values = {'J': 1, 'Q': 2, 'K': 3, 'A': 4}
        return royal_values.get(rank, 0)
    
    def handle_played_royal(self, player:Player, card:Card):
        if card.rank in ['J', 'Q', 'K', 'A']:
            self.played_royal = player
            self.cards_to_play = self.get_cards_for_royal(card.rank)
            self.next_player()
        elif self.played_royal != None:
            self.cards_to_play -= 1
            if self.cards_to_play == 0:
                print(f"{self.played_royal.name} wins royal sequence!")
                self.pile_winner = self.played_royal
                self.game_event.pile_winner = self.played_royal
    
    def reset_pile(self):
        self.pile = []
        self.burned = []
        self.played_royal = None
        self.cards_to_play = 0
        self.pile_winner = None
        self.slapped = None
        self.skip_players = set()
        self.log_card_count("Pile Taken", 0)
    
    def log_card_count(self, message,n):
        print(f"\n--- {message} ---")
        total = sum(len(p.hand) for p in self.players) + len(self.pile) + len(self.burned)
        if n == 1:
            print(f"Total cards in game: {total}")
        for player in self.players:
            print(f"{player.name}: {len(player.hand)} in hand")
        print(f"Pile: {len(self.pile)}")
        assert total == 52, f"Card count mismatch! Expected {52}, found {total}"

    def play_game(self):
        self.game_event = GameEvent(self.players[self.current_player_index])
        # Action queue is a priority queue that dequeues with the lowest reaction time
        action_queue : PriorityQueue[GameAction] = PriorityQueue(len(players))
        while len(self.players) > 1:
            # Send game event to players to get their action
            # send event in random order to breack reaction time ties
            for player in random.sample(self.players, len(self.players)):
                game_action = player.react_to_event(self.game_event)
                action_queue.put(game_action)

            # Change the players turn in the game event
            self.game_event = GameEvent(self.players[self.current_player_index]) 
            # Resolve actions in order of the queue
            while (not action_queue.empty()):
                action = action_queue.get()
                self.handle_new_action(action)

            # increment to next player in game event
            self.game_event.player_turn = self.players[self.current_player_index]

            # Check if someone slapped and won the pile
            if (self.slapped):
                # Change player turn to whoever slapped the pile
                self.current_player_index = self.players.index(self.slapped)
                self.game_event.player_turn = self.players[self.current_player_index]
                # Let player take the pile
                self.slapped.hand.extend(self.burned)
                self.slapped.hand.extend(self.pile)
                print(f"{self.slapped.name} took the pile")
                self.game_event.new_pile = True
                self.reset_pile()

            time.sleep(0.01)  # Small delay to slow down the game for readability

        if self.players:
            winner = self.players[0]
            total_cards = len(winner.hand)
            print(f"{winner.name} wins the game with {total_cards} cards!")
        else:
            print("Game over with no winners.")

        self.log_card_count("End of game",1)

class Aggressive(Player):
    def __init__(self,name):
        super().__init__(name)
        self.count=0


    def check_strategy(self,card):
        self.count+=1
        if self.count%5==0:
            print(f"Preslap! (every 5) {self.preslap()}")
        else:
            print(f"Count = {self.count}")
        pass

players = [Player("Jonathan"), Player("Dylan"), Player("Liam")]

game = Game(players)
game.play_game()

### "different inital hand states" - babe
