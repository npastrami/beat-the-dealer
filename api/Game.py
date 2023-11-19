import json
from Deck import Deck
from Dealer import Dealer
from Player import Player
from Hand import Hand
from RoundData import RoundData
from Database import Database
from ThorpStrategyBet import ThorpStrategyBet
from ThorpStrategyAction import ThorpStrategyAction

class Game:
    def __init__(self, num_decks=2, num_players=1, stop_card_index=None, user_id=None):
        self.num_decks = num_decks
        self.num_players = num_players
        self.stop_card_index = stop_card_index
        self.round_data = RoundData()
        self.database = Database(user_id)  # Assuming user_id is passed as an argument
        self.database.connect()  # Connect to the database
        self.players = []
        self.deck = None  
        self.dealer = None
        self.thorp_bet_strategy = ThorpStrategyBet()
        self.thorp_action_strategy = ThorpStrategyAction(num_decks=self.num_decks, database=self.database)
        self.round_number = 1

    def start_game(self):
        print("in start game")
        self.deck = Deck(self.num_decks)
        self.deck.shuffle()
        self.dealer = Dealer()
        self.players = [Player(f"Player {i+1}") for i in range(self.num_players)]
        self.thorp_action_strategy.database = self.database  # Make sure the database is accessible
        self.thorp_action_strategy.fetch_and_calculate_running_count()
        
    def update_running_count(self, card):
        # Example: Implement the logic to update running count based on the card
        if card.rank in ['2', '3', '4', '5', '6']:
            self.round_data.running_count += 1
        elif card.rank in ['10', 'J', 'Q', 'K', 'A']:
            self.round_data.running_count -= 1
        
        self.thorp_bet_strategy.update_running_count(self.round_data.running_count)
        
    def insert_seen_card_to_db(self, card):
        self.database.insert_seen_card(self.round_data.round_number, card)

    def deal_initial_cards(self):
        self.round_data.round_number = self.round_number
        for _ in range(2):
            for player in self.players + [self.dealer]:
                card = self.deck.deal()
                player.hands[0].add_card(card)
                self.insert_seen_card_to_db(card)  # Directly insert card to DB
                self.update_running_count(card)
                self.thorp_action_strategy.fetch_and_calculate_running_count()

        dealer_hand = self.dealer.hands[0].cards if self.dealer.hands else None
        dealer_upcard = dealer_hand[0] if dealer_hand else None
        print(f"Dealer Hand: {dealer_hand}")
        print(f"Dealer Upcard: {dealer_upcard}")
        self.calculate_and_update_recommendations(dealer_upcard)
        
    def calculate_and_update_recommendations(self, dealer_upcard):
        for player in self.players:
            recommended_bet = self.thorp_bet_strategy.recommend_bet()
            if dealer_upcard:
                recommended_action = self.thorp_action_strategy.recommend_move(player.hands[0], dealer_upcard)
            self.round_data.update_recommendations(recommended_bet, recommended_action)

    def player_action_hit(self, player_name):
        print(f"Attempting to hit for player: {player_name}")
        
        player = next((p for p in self.players if p.name == player_name), None)
        
        if not player or player.hands[0].is_busted():
            return {'error': 'Player not found or already busted'}
        
        print(f"Player {player_name} found. Dealing a card...")
        
        card_dealt = self.deck.deal()
        print(f"Card dealt: {card_dealt.suit}, {card_dealt.rank}")
        
        player.hands[0].add_card(card_dealt)# Assuming the first hand
        self.insert_seen_card_to_db(card_dealt) 
        print(f"Card added to {player_name}'s hand.")
        
        # Update RoundData
        self.round_data.update_player_hand(player_name, player.hands[0].get_cards())
        self.round_data.record_player_action(player_name, 'Hit')

        dealer_upcard = self.dealer.hands[0].cards[0]
        self.calculate_and_update_recommendations(dealer_upcard)
        
        updated_game_state = self.get_game_state()
        print(f"Updated Game State: {updated_game_state}")
        
        return updated_game_state

    def player_action_stand(self, player_name):
        player = next((p for p in self.players if p.name == player_name), None)
        if not player:
            return {'error': 'Player not found'}
        
        self.round_data.record_player_action(player_name, 'Stand')
        dealer_upcard = self.dealer.hands[0].cards[0]
        self.calculate_and_update_recommendations(dealer_upcard)
        return self.get_game_state()

    def player_action_double_down(self, player):
        if player.bet(0, player.bets[0]):  # Make sure the index 0 is used if only one hand is present
            self.player_action_hit(player.name)  # Get exactly one more card

    def dealer_action(self):
        while self.dealer.should_hit():
            new_card = self.deck.deal()
            self.dealer.hands[0].add_card(new_card)
            print(new_card.suit, new_card.rank)
            self.insert_seen_card_to_db(new_card)  # Directly insert dealer's new card to DB
            self.update_running_count(new_card)
            
    def determine_round_winner(self):
        dealer_value = self.dealer.hands[0].calculate_value()
        dealer_busted = dealer_value > 21

        for player in self.players:
            player_hand_value = player.hands[0].calculate_value()
            player_busted = player_hand_value > 21

            if player_busted:
                result = "lose"
            elif dealer_busted or player_hand_value > dealer_value:
                result = "win"
                player.win(0)  # Update player's money if they win
            elif player_hand_value == dealer_value:
                result = "push"
            else:
                result = "lose"

            self.round_data.update_round_results(
                player.name, player_hand_value, dealer_value, result
            )

        return self.round_data.round_results


    # Modify the play_round method in the Game class
    def play_round(self):
        self.deal_initial_cards()

        # Players take action
        for player in self.players:
            while player.should_hit() and not player.hands[0].is_busted():
                self.player_action_hit(player.name)
            self.player_action_stand(player.name)

        # Dealer takes action
        self.dealer_action()

        # Determine the winner and update round data
        round_results = self.determine_round_winner()

        # Export round data to a JSON file (or any other preferred method)
        with open("round_data.json", "w") as f:
            json.dump(round_results, f)

        return round_results
    
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
            'hand': [(card.suit, card.rank) for card in self.dealer.hands[0].cards],  # Updated this line
            'hand_value': self.dealer.hands[0].calculate_value(),
        }
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
                'current_bets': player.bets,
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
                'current_bet': player.bets,
            }
            for i, player in enumerate(self.players)
        ]
        return {
            'players': player_states,
        }
        
    def get_dealer_hand(self):
        dealer_state = {
            'name': self.dealer.name,
            'hand': [(card.suit, card.rank) for card in self.dealer.hands[0].cards],
            
        }
        return {
            'dealer': dealer_state,
        }
        
    def check_round_completion(self):
        all_done = all(player.has_stood or player.hands[0].is_busted() for player in self.players)
        if all_done:
            self.dealer_action()
            round_results = self.determine_round_winner()
            return round_results
        return None

    def prepare_next_round(self):
        self.round_number += 1  # Increment round number for the new round
        self.round_data.start_new_round()
        for player in self.players:
            player.reset_for_new_round()
        self.dealer.reset_for_new_round()
    
    def get_last_recommendation(self):
        # Logic to get the last recommendation based on the current state
        # For simplicity, I'm assuming you're storing the last recommendation somewhere in your class
        last_player = self.players[-1] if self.players else None
        if last_player:
            dealer_upcard = self.dealer.hands[0].cards[0] if self.dealer.hands[0].cards else None
            if dealer_upcard:
                print(f"in game method :{self.thorp_action_strategy.recommend_move(last_player.hands[0], dealer_upcard)}")
                return self.thorp_action_strategy.recommend_move(last_player.hands[0], dealer_upcard)
            else:
                return "No recommendation"