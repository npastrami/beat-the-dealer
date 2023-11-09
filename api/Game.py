import json
from Deck import Deck
from Dealer import Dealer
from Player import Player
from Hand import Hand

class Game:
    def __init__(self, num_decks=1, num_players=1, stop_card_index=None):
        self.num_decks = num_decks
        self.num_players = num_players
        self.stop_card_index = stop_card_index
        self.round_data = []
        self.players = []
        self.deck = None  
        self.dealer = None

    def start_game(self):
        self.deck = Deck(self.num_decks)
        self.deck.shuffle()
        self.dealer = Dealer()
        self.players = [Player(f"Player {i+1}") for i in range(self.num_players)]
        
    def deal_initial_cards(self):
        for _ in range(2):
            for player in self.players + [self.dealer]:
                player.hands[0].add_card(self.deck.deal())

    def player_action_hit(self, player_name):
        print(f"Attempting to hit for player: {player_name}")
        
        player = next((p for p in self.players if p.name == player_name), None)
        
        if not player:
            print(f"Player {player_name} not found.")
            return {'error': 'Player not found'}
        
        print(f"Player {player_name} found. Dealing a card...")
        
        card_dealt = self.deck.deal()
        print(f"Card dealt: {card_dealt.suit}, {card_dealt.rank}")
        
        player.hands[0].add_card(card_dealt)  # Assuming the first hand
        print(f"Card added to {player_name}'s hand.")
        
        updated_game_state = self.get_game_state()
        print(f"Updated Game State: {updated_game_state}")
        
        return updated_game_state

    def player_action_stand(self, player_name):
        player = next((p for p in self.players if p.name == player_name), None)
        print("stood")
        if not player:
            return {'error': 'Player not found'}
        
        return self.get_game_state()

    def player_action_double_down(self, player):
        if player.bet(player.current_bet):  # Double the current bet
            self.player_action_hit(player)  # Get exactly one more card

    def dealer_action(self):
        while self.dealer.should_hit():
            self.dealer.hands[0].add_card(self.deck.deal())

    def play_round(self):
        self.deal_initial_cards()

        for player in self.players:
            # Simulate player actions here (hit, stand, double down, split)
            # For this example, let's say all players hit once, then stand
            self.player_action_hit(player)
            self.player_action_stand(player)
            
            for hand in player.hands:
                # Record player state for data gathering
                self.round_data.append({
                    'player_name': player.name,
                    'player_hand_value': hand.calculate_value(),
                    'player_bet': player.current_bet
                })

        # Dealer takes action
        self.dealer_action()
        
        # Record dealer state for data gathering
        self.round_data.append({
            'dealer_name': self.dealer.name,
            'dealer_hand_value': self.dealer.hand.calculate_value()
        })

        # Export round data to a JSON file (or any other preferred method)
        with open("round_data.json", "w") as f:
            json.dump(self.round_data, f)

        return self.round_data
    
    def player_action_split(self, player, hand_index):
        # Check if the player can split the hand (must have two cards of the same rank)
        hand = player.hands[hand_index]
        if len(hand.cards) != 2 or hand.cards[0].rank != hand.cards[1].rank:
            return False  # Cannot split

        # Create a new hand with one of the cards from the original hand
        new_hand = Hand()
        new_hand.add_card(hand.cards.pop())

        # Add the new hand to the player's hands and adjust bets
        player.add_hand()
        player.hands[-1] = new_hand

        return True  # Successfully split
    
    def get_game_state(self):
        dealer_state = {
            'name': self.dealer.name,
            'hand': [(card.suit, card.rank) for card in self.dealer.hands[0].cards]  # Updated this line
        }
        player_states = [
            {
                'player_id': i,
                'name': player.name,
                'hands': [
                    {
                        'hand_index': j,
                        'cards': [(card.suit, card.rank) for card in hand.cards],
                    }
                    for j, hand in enumerate(player.hands)
                ],
                'chips': player.money,
                'current_bet': player.current_bet,
            }
            for i, player in enumerate(self.players)
        ]
        return {
            'dealer': dealer_state,
            'players': player_states,
        }
        
    def get_player_hand(self):
        player_states = [
            {
                'player_id': i,
                'name': player.name,
                'hands': [
                    {
                        'hand_index': j,
                        'hand_value': hand.calculate_value(),
                        'cards': [(card.suit, card.rank) for card in hand.cards],
                    }
                    for j, hand in enumerate(player.hands)
                ],
                'chips': player.money,
                'current_bet': player.current_bet,
            }
            for i, player in enumerate(self.players)
        ]
        return {
            'players': player_states,
        }
        
    def get_dealer_hand(self):
        dealer_state = {
            'name': self.dealer.name,
            'hand': [(card.suit, card.rank) for card in self.dealer.hands[0].cards]  # Updated this line
        }
        return {
            'dealer': dealer_state,
        }