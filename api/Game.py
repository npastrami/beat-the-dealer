import json
from Card import Card
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
        self.thorp_action_strategy = ThorpStrategyAction(num_decks=self.num_decks, stop_card_index=self.stop_card_index, database=self.database)
        self.round_number = 1
        self.reshuffle_number = 1
        self.stop_card_index = stop_card_index
        self.stop_card_position = int((stop_card_index / 100) * num_decks * 52)  # Convert percentage to the card number
        print(f"stop card index: {stop_card_index}")

    def start_game(self):
        print("in start game")
        self.deck = Deck(self.num_decks, self.stop_card_position)
        self.deck.shuffle()
        self.deck.set_stop_card_position(self.stop_card_position)
        self.dealer = Dealer()
        self.players = [Player(f"Player {i+1}") for i in range(self.num_players)]
        self.thorp_action_strategy.database = self.database  # Make sure the database is accessible
        self.thorp_action_strategy.fetch_and_calculate_running_count(self.reshuffle_number, self.deck.stop_card_position)
        print(f"start game decks: {self.num_decks}, stop card position: {self.stop_card_index}, {self.stop_card_position}")
        
    def update_running_count(self, card):
        # Example: Implement the logic to update running count based on the card
        if card.rank in ['2', '3', '4', '5', '6']:
            self.round_data.running_count += 1
        elif card.rank in ['10', 'J', 'Q', 'K', 'A']:
            self.round_data.running_count -= 1
        
        self.thorp_bet_strategy.update_running_count(self.round_data.running_count)
        
    def insert_seen_card_to_db(self, card):
        self.database.insert_seen_card(self.round_data.round_number, self.reshuffle_number, card)
        
    def deal_card(self, player, hand_index=0):
        if self.deck.is_time_to_shuffle():
            self.reshuffle_deck()
        card = self.deck.deal()
        player.hands[hand_index].add_card(card)
        self.insert_seen_card_to_db(card)
        self.update_running_count(card)
        # Pass the current stop card position to the method
        self.thorp_action_strategy.fetch_and_calculate_running_count(self.reshuffle_number, self.deck.stop_card_position)

    def deal_initial_cards(self):
        self.round_data.round_number = self.round_number
        for _ in range(2):
            for player in self.players + [self.dealer]:
                self.deal_card(player)

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

    def get_player_by_name(self, name):
        return next((p for p in self.players if p.name == name), None)

    def player_action_hit(self, player_name):
        player = self.get_player_by_name(player_name)
        if not player or player.active_hand_index >= len(player.hands):
            return {'error': 'Invalid hand index or player not found'}

        active_hand = player.hands[player.active_hand_index]
        if active_hand.is_busted():
            return {'error': 'Hand already busted'}

        card_dealt = self.deck.deal()
        active_hand.add_card(card_dealt)
        self.insert_seen_card_to_db(card_dealt)
        self.update_running_count(card_dealt)

        self.round_data.update_player_hand(player_name, active_hand.get_cards())
        self.round_data.record_player_action(player_name, 'Hit')

        if active_hand.is_busted() and player.has_more_hands():
            player.next_hand()

        print(f"Player {player_name} hit on hand {player.active_hand_index}")

        return self.get_game_state()

    def player_action_stand(self, player_name):
        player = self.get_player_by_name(player_name)
        if not player:
            return {'error': 'Player not found'}

        active_hand = player.hands[player.active_hand_index]
        active_hand.stand()

        print(f"Player {player_name} has stood on hand {player.active_hand_index}.")

        if player.has_more_hands():
            player.next_hand()
        else:
            if player.all_hands_stood_or_busted():
                print(f"All hands of {player_name} have stood or busted.")
            return self.get_game_state()

        return self.get_game_state()

    def are_all_players_done(self):
        return all(player.has_stood for player in self.players)

    def player_action_double_down(self, player_name):
        player = next((p for p in self.players if p.name == player_name), None)
        if not player:
            return {'error': 'Player not found'}

        # Double the bet amount for the first hand
        hand_index = 0  # Assuming the first hand for doubling down
        current_bet = player.bets[hand_index]
        if not player.bet(hand_index, current_bet):
            return {'error': 'Insufficient funds to double down'}

        # Deal one more card to the player's hand
        self.deal_card(player)

        # Mark the player's turn as complete
        player.has_stood = True

        # Update game state and return it
        updated_game_state = self.get_game_state()
        return updated_game_state

    def dealer_action(self):
        while self.dealer.should_hit():
            new_card = self.deck.deal()
            self.dealer.hands[0].add_card(new_card)
            print(new_card.suit, new_card.rank)
            self.insert_seen_card_to_db(new_card)  # Directly insert dealer's new card to DB
            self.update_running_count(new_card)
        return self.get_game_state()
            
    def determine_round_winner(self):
        dealer_value = self.dealer.hands[0].calculate_value()
        dealer_busted = dealer_value > 21

        for player in self.players:
            for hand_index, hand in enumerate(player.hands):
                player_hand_value = hand.calculate_value()
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
                    
                # Print the result for each hand
                print(f"{player.name} Hand {hand_index}: {player_hand_value} vs Dealer: {dealer_value} - {result}")

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
        hand = player.hands[hand_index]
        if not player.hands[hand_index].can_split():
            return False  # Cannot split

        # Create a new hand with one of the cards from the original hand
        new_hand = Hand()
        new_hand.add_card(hand.cards.pop())

        # Add the new hand to the player's hands and duplicate the bet for the new hand
        player.hands.append(new_hand)
        player.bets.append(player.bets[hand_index])
        player.active_hand_index = 0
        
        # if not player.place_bet_for_split(hand_index):
        #     return {'error': 'Insufficient funds to place bet for split'}

        # Deal a new card to both the original hand and the new hand
        self.deal_card(player, hand_index)
        self.deal_card(player, len(player.hands) - 1)  # The index of the new hand

        return True
    
    def get_game_state(self):
        dealer_state = {
            'name': self.dealer.name,
            'hand': [(card.suit, card.rank) for card in self.dealer.hands[0].cards],  # Updated this line
            'hand_value': self.dealer.hands[0].calculate_value(),
        }
        player_states = [
            {
                'name': player.name,
                'hands': [
                    {
                        'hand_value': hand.calculate_value(),
                        'cards': [(card.suit, card.rank) for card in hand.cards],
                    }
                    for hand in player.hands
                ],
                'chips': player.money,
                'current_bets': player.bets,
            }
            for player in self.players
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
        print("Checking if all players are done...")

        all_done = all(player.all_hands_stood_or_busted() for player in self.players)

        if all_done:
            print("All players are done. Proceeding to dealer's turn.")
            self.dealer_action()
            round_results = self.determine_round_winner()
            return {'roundResults': round_results, 'gameState': self.get_game_state()}
        else:
            print("Not all players are done. Continuing the round.")
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
            
    def reshuffle_deck(self, new_stop_card_position_percent):
        # Bring back all seen cards
        seen_cards = self.database.fetch_seen_cards_for_reshuffle(self.reshuffle_number)
        for card_info in seen_cards:
            self.deck.add_card(Card(card_info['suit'], card_info['rank']))

        # Reset seen cards in the database and increment reshuffle number
        self.database.increment_reshuffle_number(self.round_number)

        # Update stop card position
        total_deck_cards = 52 * self.num_decks
        self.stop_card_position = int((new_stop_card_position_percent / 100) * total_deck_cards)
        self.deck.rebuild_deck(self.num_decks, self.stop_card_position)
        self.deck.shuffle()
        self.deck.reset_count()

        # Reset the running count & Update stop card index in ThorpStrategyAction
        self.thorp_action_strategy.update_stop_card_index(new_stop_card_position_percent)
        self.thorp_action_strategy.reset_running_count()
        self.thorp_action_strategy.fetch_and_calculate_running_count(self.reshuffle_number, self.deck.stop_card_position)
        self.reshuffle_number += 1