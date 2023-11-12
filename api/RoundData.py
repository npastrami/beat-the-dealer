class RoundData:
    def __init__(self):
        self.round_number = 0
        self.player_hands = {}  # Current player hands
        self.dealer_hand = []   # Current dealer hand
        self.player_bets = {}   # Player bets
        self.player_actions = {}  # Player actions
        self.seen_cards = []    # Cards seen in the deck
        self.running_count = 0  # Running count for card counting

    def start_new_round(self):
        self.round_number += 1
        self.player_hands = {}
        self.dealer_hand = []
        self.player_bets = {}
        self.player_actions = {}
        self.seen_cards = []

    def update_player_hand(self, player_name, hand):
        self.player_hands[player_name] = hand

    def update_dealer_hand(self, hand):
        self.dealer_hand = hand

    def update_player_bet(self, player_name, bet):
        self.player_bets[player_name] = bet

    def record_player_action(self, player_name, action):
        if player_name not in self.player_actions:
            self.player_actions[player_name] = []
        self.player_actions[player_name].append(action)
        
    def update_round_results(self, player_name, player_hand_value, dealer_hand_value, result):
        if 'round_results' not in self.__dict__:
            self.round_results = []

        self.round_results.append({
            'player_name': player_name,
            'player_hand_value': player_hand_value,
            'dealer_hand_value': dealer_hand_value,
            'result': result
        })
    
    def update_running_count(self, count):
        self.running_count = count
        
    def update_recommendations(self, recommended_bet, recommended_action):
        self.recommended_bet = recommended_bet
        self.recommended_action = recommended_action