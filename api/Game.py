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
        
        if not player or player.hands[0].is_busted():
            return {'error': 'Player not found or already busted'}
        
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
        if player.bet(0, player.bets[0]):  # Make sure the index 0 is used if only one hand is present
            self.player_action_hit(player.name)  # Get exactly one more card

    def dealer_action(self):
        while self.dealer.should_hit():
            new_card = self.deck.deal()
            print(f"Dealer hits: {new_card.suit}, {new_card.rank}")
            self.dealer.hands[0].add_card(new_card)
            
    def determine_round_winner(self):
        # This method assumes that the dealer has already played their hand
        dealer_value = self.dealer.hands[0].calculate_value()
        print(dealer_value)
        dealer_busted = dealer_value > 21

        for player in self.players:
            player_hand_value = player.hands[0].calculate_value()
            print(player_hand_value) # Assuming only one hand per player
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

            # Update round_data with the results of this round
            self.round_data.append({
                'player_name': player.name,
                'player_hand_value': player_hand_value,
                'dealer_hand_value': dealer_value,
                'result': result
            })

        # Return round data with the results
        return self.round_data


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
        # Check if all players have finished their actions
        all_done = all(player.has_stood or player.hands[0].is_busted() for player in self.players)

        if all_done:
            # Perform dealer actions if all players are done
            self.dealer_action()

            # Determine the winner of the round
            round_results = self.determine_round_winner()

            # Optionally, prepare for the next round
            self.prepare_next_round()

            return round_results

        return None  # If the round is not complete, return None
    
    def prepare_next_round(self):
        # Reset the round data
        self.round_data = []

        # Clear players' hands and reset their status
        for player in self.players:
            player.reset_for_new_round()

        # Clear dealer's hand
        self.dealer.reset_for_new_round()

        # Deal new cards
        self.deal_initial_cards()