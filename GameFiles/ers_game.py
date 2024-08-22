from queue import PriorityQueue
import random
from GameFiles.game_action import GameAction
from GameFiles.game_event import GameEvent
from GameFiles.card import Card
from Players.player import Player

## Representation of game logic
class Game:
    def __init__(self,players, print_messages=False):
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
        self.print_messages = print_messages

        #Deal the cards
        self.create_deck()

    def custom_print(self, message):
        if self.print_messages: print(message)

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
                self.handle_new_card(action.player, card)
                if (len(action.player.hand) == 0):
                    self.temp_remove_player(action.player)
            case "Slap":
                self.handle_slap(action.player)
            case "Leave":
                self.full_remove_player(action.player)
            case _:
                pass

    # Handle a players slap
    def handle_slap(self, player):
        self.custom_print(f"{player.name} slapped the pile")
        # Handle when the miss slap and have to burn
        if not self.is_slappable(player):
            burned_card = player.get_top_card()
            # Check if they have a card to burn
            if (burned_card == None):
                self.custom_print(f"{player.name} used their last slap")
                return
            # Burn the card
            self.custom_print(f"{player.name} burned the {burned_card} because they slapped the pile")
            self.burned.append(burned_card)
            self.game_event.burned.append(burned_card)
            # If they run out of cards temporarily remove them from rotation till next pile
            if (len(player.hand) == 0):
                self.temp_remove_player(player)
            return
        # Handle when they slap first
        if not self.slapped:
            self.slapped = player
        # Handle when they slap after someone else
        else:
            pass

    # Handle player playing card
    def handle_new_card(self, player, card):
        self.custom_print(f"{player.name} played the {card}")
        # Check if they played out of turn then they burn
        if self.players[self.current_player_index] != player:
            self.custom_print(f"{player.name} burned the {card} because they were out of turn")
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
                self.custom_print(f"{self.played_royal.name} wins royal sequence!")
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

    # Temporarily remove player until the next round if they run out of cards
    def temp_remove_player(self, player):
        self.custom_print(f"{player.name} has no more cards")
        # If played last card during a royal sequence
        # whoever played the royal wins that pile
        if self.played_royal:
            if (self.cards_to_play != 0):
                self.custom_print(f"{self.played_royal.name} wins royal sequence!")
            self.pile_winner = self.played_royal
            self.game_event.pile_winner = self.played_royal
            return
        # If there was no royal played then that players turn is skipped
        self.skip_players.add(player)
        # Check if there is only 1 player left
        if (len(self.players) - len(self.skip_players) == 1):
            # Find the last player
            last_player = None
            for player in self.players:
                if (player not in self.skip_players):
                    last_player = player
                    break
            # Give the pile to the last player
            last_player.hand.extend(self.burned)
            last_player.hand.extend(self.pile)
            self.custom_print(f"{last_player.name} took the pile")
            self.game_event.new_pile = True
            self.current_player_index = self.players.index(last_player)
            self.game_event.movements = []
            self.reset_pile()
            return
        # If there are more players if the player removed was supposed to play
        # Go to the next person in rotation
        if (self.players[self.current_player_index] == player):
            self.next_player()

    # Fully remove player from rotation
    def full_remove_player(self, player):
        self.custom_print(f"{player.name} is out of the game")
        self.players.remove(player)
        self.current_player_index = self.players.index(self.game_event.player_turn)
    
    def log_card_count(self, message,n):
        self.custom_print(f"\n--- {message} ---")
        total = sum(len(p.hand) for p in self.players) + len(self.pile) + len(self.burned)
        if n == 1:
            self.custom_print(f"Total cards in game: {total}")
        for player in self.players:
            self.custom_print(f"{player.name}: {len(player.hand)} in hand")
        self.custom_print(f"Pile: {len(self.pile)}")
        assert total == 52, f"Card count mismatch! Expected {52}, found {total}"

    # Main game loop
    def play_game(self):
        # Initial game start event
        self.game_event = GameEvent(self.players[self.current_player_index])
        # Give the players the current rotation after filtering the skipped players
        self.game_event.player_rotation = list(filter(lambda player: player not in self.skip_players, self.players))
        # Action queue is a priority queue that dequeues with the lowest reaction time
        action_queue : PriorityQueue[GameAction] = PriorityQueue(len(self.players))
        while len(self.players) > 1:
            # Send game event to players to get their action
            # send event in random order to break reaction time ties
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
                self.custom_print(f"{self.slapped.name} took the pile")
                self.game_event.new_pile = True
                self.game_event.movements = []
                self.reset_pile()
                
            # Give the players the current rotation after filtering the skipped players
            self.game_event.player_rotation = list(filter(lambda player: player not in self.skip_players, self.players))

        if self.players:
            winner = self.players[0]
            total_cards = len(winner.hand)
            self.custom_print(f"{winner.name} wins the game with {total_cards} cards!")
        else:
            self.custom_print("Game over with no winners.")

        self.log_card_count("End of game",1)
        return self.players[0]
