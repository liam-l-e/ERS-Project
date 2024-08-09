import random
import time

## Card representation with rank and suit
class Card:
    def __init__(self,rank,suit):
        self.rank=rank
        self.suit=suit

    def __str__(self):
        return f"{self.rank} of {self.suit}"

## Player representation with name,hand,and play first card
class Player:
    def __init__(self,  name):
        self.name = name
        self.main_hand = []
        self.won_cards = []
        self.reaction_time = random.uniform(0.1,0.5)

    def attempt_slap(self):
        if random.random() <0.8:
            slap_time = self.reaction_time + random.uniform(0,0.1) ## Random on random reaction time
            return slap_time
        return None

    def play_card(self):
        if not self.main_hand:
            self.shuffle_won_cards()
        if self.main_hand:        
            return self.main_hand.pop(0)
        return None
    
    def shuffle_won_cards(self):
        random.shuffle(self.won_cards)
        self.main_hand.extend(self.won_cards)
        self.won_cards = []


## Representation of game logic
class Game:
    def __init__(self,players):
        self.players=players
        self.pile = []
        self.pot = []
        self.create_deck()
        self.current_player_index = 0
        self.played_royal = None
        self.cards_to_play = 0
        self.total_cards = 52
        self.pile_winner = None

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
            player.main_hand = [deck.pop() for _ in range(cards_per_player)]

        # Place remaining card(s) in the pile to start the game
        self.pile = [deck.pop() for _ in range(remainder)]

        self.log_card_count("After initial deal",1)

    def log_card_count(self, message,n):
        print(f"\n--- {message} ---")
        total = sum(len(p.main_hand) + len(p.won_cards) for p in self.players) + len(self.pile) + len(self.pot)
        if n == 1:
            print(f"Total cards in game: {total}")
        for player in self.players:
            print(f"{player.name}: {len(player.main_hand)+len(player.won_cards)} in hand")
        print(f"Pile: {len(self.pile)}")
        assert total == 52, f"Card count mismatch! Expected {52}, found {total}"

    def play_round(self):
        self.pile_winner = None
        while True:
            if not self.players:
                return True
            
            player = self.players[self.current_player_index]
            card = player.play_card()
            
            if card:
                self.pile.append(card)
                print(f"{player.name} plays {card}")
                
                if self.check_slap():
                    self.played_royal = None
                    self.cards_to_play = 0
                    self.next_player()
                    return True  # Someone won the pile
                
                if self.handle_played_royal(player,card):
                    self.next_player()
                    return True
                
                if self.played_royal==None:
                    self.next_player()

            else:
                if not player.main_hand and not player.won_cards: # Out of game logic
                    print(f"{player.name} is out of the game!")
                    self.players.pop(self.current_player_index)
                    if len(self.players) <= 1:
                        return True  # Game over
                    self.current_player_index %= len(self.players)
                else:

                    self.next_player()
            
            if len(self.players) == 1:
                return True  # Game over
            
            if self.played_royal!= None:
                break
        
        return False
    
    def next_player(self):
        if self.pile_winner:
            index = self.players.index(self.pile_winner)
            self.current_player_index = index
        else:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
    
    def check_slap(self):
        if self.is_slappable():
            slap_window = 1.0  # 1 second window to slap
            slap_attempts = []

            for player in self.players:
                slap_time = player.attempt_slap()
                if slap_time is not None and slap_time < slap_window:
                    slap_attempts.append((player, slap_time))

            if slap_attempts:
                winner, _ = min(slap_attempts, key=lambda x: x[1])
                winner.main_hand.extend(self.pile)
                print(f"{winner.name} slaps and wins the pile in by {self.is_slappable()} {_:.3f} seconds!")
                self.pile = []
                self.pile_winner = winner
                return True

        return False

    ## Slap logic (doubles, sandwiches, marriages)
    def is_slappable(self):
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
                
        return False
    
    def get_cards_for_royal(self,rank):
        royal_values = {'J': 1, 'Q': 2, 'K': 3, 'A': 4}
        return royal_values.get(rank, 0)
    
    def handle_played_royal(self, player, card):
        if card.rank in ['J', 'Q', 'K', 'A']:
            self.played_royal = player
            self.cards_to_play = self.get_cards_for_royal(card.rank)
            self.next_player()
            # print(f"{player.name} played a {card.rank}! Next player must play {self.cards_to_play} cards.")
        elif self.played_royal != None: #
            self.cards_to_play -= 1
            if self.cards_to_play == 0:
                self.played_royal.won_cards.extend(self.pile)
                self.pile = []
                print(f"{self.played_royal.name} wins royal sequence!")
                self.pile_winner = self.played_royal
                self.played_royal=None
                return True
            
        return False


    def play_game(self):
        while len(self.players) > 1:
            if self.play_round():
                self.log_card_count("",0)
                if len(self.players) <= 1:
                    break
            time.sleep(0.01)  # Small delay to slow down the game for readability

        if self.players:
            winner = self.players[0]
            total_cards = len(winner.main_hand) + len(winner.won_cards)
            print(f"{winner.name} wins the game with {total_cards} cards!")
        else:
            print("Game over with no winners.")

        self.log_card_count("End of game",1)

players = [Player("Jonathan"), Player("Dylan"), Player("Liam")]

game = Game(players)
game.play_game()