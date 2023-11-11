class RoundData:
    def __init__(self):
        self.round_number = 0
        self.player_hands = {}  # Store cards for each player's hand
        self.dealer_hand = []   # Store cards for the dealer's hand
        self.player_bets = {}   # Store bets for each player
        self.player_actions = {}  # Store actions taken by each player

    def start_new_round(self):
        self.round_number += 1
        self.player_hands = {}
        self.dealer_hand = []
        self.player_bets = {}
        self.player_actions = {}

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