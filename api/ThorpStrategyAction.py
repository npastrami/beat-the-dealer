from Database import Database

class ThorpStrategyAction:
    def __init__(self, num_decks=1, stop_card_index=0.5, database=None):
        """
        Initializes the Thorp Strategy Action class.
        :param num_decks: Number of decks being used.
        :param stop_card_index: The position of the stop card as a decimal (e.g., 0.75 for 75% through the deck).
        :param database: Instance of the database class for fetching seen cards.
        """
        self.total_points = 0
        self.stop_card_index = stop_card_index  # Ensure this is a decimal representing the percentage (0 to 1)
        self.total_unseen_cards = int(52 * num_decks * ((self.stop_card_index)/100))  # Calculate total unseen cards based on stop card position
        self.high_low_index = 0
        self.num_decks = num_decks
        self.database = database

    def fetch_and_calculate_running_count(self):
        """
        Fetches all seen cards from the database and calculates the running count.
        """
        seen_cards = self.database.fetch_all_seen_cards()
        print("Seen cards fetched:", seen_cards)
        self.total_points = sum(
            1 if card['rank'] in ['2', '3', '4', '5', '6'] else
            -1 if card['rank'] in ['10', 'J', 'Q', 'K', 'A'] else
            0
            for card in seen_cards
        )
        self.total_unseen_cards = 52 * self.num_decks * ((self.stop_card_index)/100) - len(seen_cards)
        self.calculate_high_low_index()
        
    def calculate_high_low_index(self):
        """
        Calculates the high-low index based on current counts.
        """
        if self.total_unseen_cards > 0:
            self.high_low_index = self.total_points / self.total_unseen_cards
        else:
            self.high_low_index = 0
        print(f"New High-Low Index: {self.high_low_index}")

        self.high_low_index *= 100

    def recommend_bet(self):
        """
        Recommends a bet size based on the current high-low index.
        :return: Recommended bet size.
        """
        if self.high_low_index > 2:
            return 2 
        elif self.high_low_index > 4:
            return 3  
        elif self.high_low_index > 6:
            return 4  
        else:
            return 1  

    def recommend_move(self, player_hand, dealer_upcard):
        player_total = player_hand.calculate_value()
        dealer_upcard_value = str(dealer_upcard.point_value)
        print(f"Dealer upcard: {dealer_upcard.suit}, {dealer_upcard.rank}")
        print(f"Current Hi-Lo Count: {self.high_low_index}")
        
        print(F"Total unseen cards: {self.total_unseen_cards}")
        is_soft_hand = player_hand.is_soft()
        can_split = player_hand.can_split()

        # Logic for hard hands
        if not is_soft_hand and not can_split:
            decision_threshold = hard_hand_decision_dict.get(player_total, {}).get(dealer_upcard_value)
            print(f"7.1 Decision_Threshold: {decision_threshold}, player total: {player_total}, dealer upcard: {dealer_upcard_value}")
            if decision_threshold is not None:
                return 'Hit 7.1' if self.high_low_index <= decision_threshold else 'Stand 7.1'
        # Logic for soft hands
        elif is_soft_hand:
            decision_threshold = soft_hand_decision_dict.get(player_total, {}).get(dealer_upcard_value)
            print(f"7.2 Decision_Threshold: {decision_threshold}, player total: {player_total}, dealer upcard: {dealer_upcard_value}")
            if decision_threshold is not None:
                return 'Hit 7.2' if self.high_low_index <= decision_threshold else 'Stand 7.2'
        # Logic for hard doubling down
        if not is_soft_hand and not can_split and player_total in [9, 10, 11]:
            decision_threshold = hard_double_decision_dict.get((player_total, dealer_upcard_value))
            print(f"7.3 Decision_Threshold: {decision_threshold}, player total: {player_total}, dealer upcard: {dealer_upcard_value}")
            if decision_threshold is not None:
                return 'Double 7.3' if self.high_low_index > decision_threshold else 'Hit 7.3'
        # Logic for soft doubling down
        if is_soft_hand and player_total in range(12, 22):  # Ace valued as 11, hence range 12 to 21
            player_hand_key = 'A,' + str(player_total - 11)
            decision_threshold = soft_double_decision_dict.get((player_hand_key, dealer_upcard_value))
            print(f"7.4 Decision_Threshold: {decision_threshold}, player total: {player_total}, dealer upcard: {dealer_upcard_value}")
            if decision_threshold is not None:
                if isinstance(decision_threshold, list):
                    if decision_threshold[0] <= self.high_low_index <= decision_threshold[1]:
                        return 'Double 7.4'
                elif self.high_low_index > decision_threshold:
                    return 'Double 7.4'
        # Logic for splitting pairs
        if can_split:
            player_hand_key = ','.join(sorted([str(card.rank) for card in player_hand.cards]))
            decision_threshold = split_decision_dict.get((player_hand_key, dealer_upcard_value))
            print(f"7.5 Decision_Threshold: {decision_threshold}, player total: {player_total}, dealer upcard: {dealer_upcard_value}")
            if decision_threshold is not None:
                if isinstance(decision_threshold, list):
                    if decision_threshold[0] <= self.high_low_index <= decision_threshold[1]:
                        return 'Split 7.5'
                elif self.high_low_index > decision_threshold:
                    return 'Split 7.5'
                
        if is_soft_hand and player_total <= 16:
            return 'Hit 7.2.2'

        # If no other action is recommended, default to stand
        return 'Stand general'

    def adjust_for_seen_card(self, card):
        """
        Adjusts the counts based on a seen card.
        :param card: The card that has been seen.
        """
        self.fetch_and_calculate_running_count(card)
        
hard_hand_decision_dict = {
    21: {'2': None, '3': None, '4': None, '5': None, '6': None, '7': None, '8': None, '9': None, '10': None, '11': None},
    20: {'2': None, '3': None, '4': None, '5': None, '6': None, '7': None, '8': None, '9': None, '10': None, '11': None},
    19: {'2': None, '3': None, '4': None, '5': None, '6': None, '7': None, '8': None, '9': None, '10': None, '11': None},
    18: {'2': None, '3': None, '4': None, '5': None, '6': None, '7': None, '8': None, '9': None, '10': None, '11': None},
    17: {'2': None, '3': None, '4': None, '5': None, '6': None, '7': None, '8': None, '9': None, '10': None, '11': -15},
    16: {'2': -21, '3': -25, '4': -30, '5': -34, '6': -35, '7': 10, '8': 11, '9': 6, '10': 2, '11': 14},
    15: {'2': -12, '3': -17, '4': -21, '5': -26, '6': -28, '7': 13, '8': 15, '9': 12, '10': 8, '11': 16},
    14: {'2': -5, '3': -8, '4': -13, '5': -17, '6': -17, '7': 20, '8': 38, '9': 100, '10': 100, '11': 100},
    13: {'2': 1, '3': -2, '4': -5, '5': -9, '6': -8, '7': 50, '8': 100, '9': 100, '10': 100, '11': 100},
    12: {'2': 14, '3': 6, '4': 2, '5': -1, '6': 0, '7': 100, '8': 100, '9': 100, '10': 100, '11': 100},
    11: {'2': 100, '3': 100, '4': 100, '5': 100, '6': 100, '7': 100, '8': 100, '9': 100, '10': 100, '11': 100},
    10: {'2': 100, '3': 100, '4': 100, '5': 100, '6': 100, '7': 100, '8': 100, '9': 100, '10': 100, '11': 100},
    9: {'2': 100, '3': 100, '4': 100, '5': 100, '6': 100, '7': 100, '8': 100, '9': 100, '10': 100, '11': 100},
    8: {'2': 100, '3': 100, '4': 100, '5': 100, '6': 100, '7': 100, '8': 100, '9': 100, '10': 100, '11': 100},
    7: {'2': 100, '3': 100, '4': 100, '5': 100, '6': 100, '7': 100, '8': 100, '9': 100, '10': 100, '11': 100},
    6: {'2': 100, '3': 100, '4': 100, '5': 100, '6': 100, '7': 100, '8': 100, '9': 100, '10': 100, '11': 100},
    5: {'2': 100, '3': 100, '4': 100, '5': 100, '6': 100, '7': 100, '8': 100, '9': 100, '10': 100, '11': 100},
    4: {'2': 100, '3': 100, '4': 100, '5': 100, '6': 100, '7': 100, '8': 100, '9': 100, '10': 100, '11': 100},
    3: {'2': 100, '3': 100, '4': 100, '5': 100, '6': 100, '7': 100, '8': 100, '9': 100, '10': 100, '11': 100},
    2: {'2': 100, '3': 100, '4': 100, '5': 100, '6': 100, '7': 100, '8': 100, '9': 100, '10': 100, '11': 100},
    
}

soft_hand_decision_dict = {
    21: {'2': None, '3': None, '4': None, '5': None, '6': None, '7': None, '8': None, '9': None, '10': None, '11': None},
    20: {'2': None, '3': None, '4': None, '5': None, '6': None, '7': None, '8': None, '9': None, '10': None, '11': None},
    19: {'2': None, '3': None, '4': None, '5': None, '6': None, '7': None, '8': None, '9': None, '10': None, '11': None},
    18: {'2': None, '3': None, '4': None, '5': None, '6': None, '7': None, '8': None, '9': 100, '10': 12, '11': -6},
    17: {'2': 100, '3': 100, '4': 100, '5': 100, '6': 100, '7': 29, '8': 100, '9': 100, '10': 100, '11': 100}, 
    16: {'2': 100, '3': 100, '4': 100, '5': 100, '6': 100, '7': 100, '8': 100, '9': 100, '10': 100, '11': 100},
    15: {'2': 100, '3': 100, '4': 100, '5': 100, '6': 100, '7': 100, '8': 100, '9': 100, '10': 100, '11': 100},
    14: {'2': 100, '3': 100, '4': 100, '5': 100, '6': 100, '7': 100, '8': 100, '9': 100, '10': 100, '11': 100},
    13: {'2': 100, '3': 100, '4': 100, '5': 100, '6': 100, '7': 100, '8': 100, '9': 100, '10': 100, '11': 100},
    12: {'2': 100, '3': 100, '4': 100, '5': 100, '6': 100, '7': 100, '8': 100, '9': 100, '10': 100, '11': 100},
    11: {'2': 100, '3': 100, '4': 100, '5': 100, '6': 100, '7': 100, '8': 100, '9': 100, '10': 100, '11': 100},
    10: {'2': 100, '3': 100, '4': 100, '5': 100, '6': 100, '7': 100, '8': 100, '9': 100, '10': 100, '11': 100},
    9: {'2': 100, '3': 100, '4': 100, '5': 100, '6': 100, '7': 100, '8': 100, '9': 100, '10': 100, '11': 100},
    8: {'2': 100, '3': 100, '4': 100, '5': 100, '6': 100, '7': 100, '8': 100, '9': 100, '10': 100, '11': 100},
    7: {'2': 100, '3': 100, '4': 100, '5': 100, '6': 100, '7': 100, '8': 100, '9': 100, '10': 100, '11': 100},
    6: {'2': 100, '3': 100, '4': 100, '5': 100, '6': 100, '7': 100, '8': 100, '9': 100, '10': 100, '11': 100},
    5: {'2': 100, '3': 100, '4': 100, '5': 100, '6': 100, '7': 100, '8': 100, '9': 100, '10': 100, '11': 100},
    4: {'2': 100, '3': 100, '4': 100, '5': 100, '6': 100, '7': 100, '8': 100, '9': 100, '10': 100, '11': 100},
    3: {'2': 100, '3': 100, '4': 100, '5': 100, '6': 100, '7': 100, '8': 100, '9': 100, '10': 100, '11': 100},
    2: {'2': 100, '3': 100, '4': 100, '5': 100, '6': 100, '7': 100, '8': 100, '9': 100, '10': 100, '11': 100},
    
    

}

hard_double_decision_dict = {
    (11, '2'): -23, (11, '3'): -26, (11, '4'): -29, (11, '5'): -33, (11, '6'): -35,
    (11, '7'): -26, (11, '8'): -16, (11, '9'): -10, (11, '10'): -9, (11, 'A'): -3,
    (10, '2'): -15, (10, '3'): -17, (10, '4'): -21, (10, '5'): -24, (10, '6'): -26,
    (10, '7'): -17, (10, '8'): -9,  (10, '9'): -3,  (10, '10'): 7,  (10, 'A'): 6,
    (9, '2'): 3,   (9, '3'): 0,    (9, '4'): -5,   (9, '5'): -10,  (9, '6'): -12,
    (9, '7'): 4,   (9, '8'): 14,
    (8, '3'): 22,  (8, '4'): 11,   (8, '5'): 5,    (8, '6'): 5,    (8, '7'): 22,
    (7, '4'): 45,  (7, '5'): 21,   (7, '6'): 14,   (7, '7'): 17,
    (6, '5'): 27,  (6, '6'): 18,   (6, '7'): 24,
    (5, '6'): 20,  (5, '7'): 26,
}

soft_double_decision_dict = {
    ('A,9', '2'): 20, ('A,9', '3'): 12, ('A,9', '4'): 8, ('A,9', '5'): 8, ('A,9', '6'): 8,
    ('A,8', '3'): 9, ('A,8', '4'): 5, ('A,8', '5'): 1, ('A,8', '6'): 0,
    ('A,7', '2'): -2, ('A,7', '3'): -15, ('A,7', '4'): -18, ('A,7', '5'): -23, ('A,7', '6'): -23,
    ('A,6', '2'): [1, 10],  # Special case: double down only when index is between 1 and 10
    ('A,6', '3'): -8, ('A,6', '4'): -14, ('A,6', '5'): -28, ('A,6', '6'): -30,
    ('A,5', '2'): 21, ('A,5', '3'): -6, ('A,5', '4'): -16, ('A,5', '5'): -32, ('A,5', '6'): -32,
    ('A,4', '2'): 19, ('A,4', '3'): -7, ('A,4', '4'): -16, ('A,4', '5'): -23, ('A,4', '6'): -23,
    ('A,3', '2'): 11, ('A,3', '3'): -3, ('A,3', '4'): -13, ('A,3', '5'): -19, ('A,3', '6'): -19,
    ('A,2', '2'): 10, ('A,2', '3'): 2,  ('A,2', '4'): -19, ('A,2', '5'): -13, ('A,2', '6'): -13,
}

split_decision_dict = {
    'A,A': {'2': -100, '3': -100, '4': -100, '5': -100, '6': -100, '7': -33, '8': -24, '9': -22, '10': -20, 'A': -17},
    '10,10': {'2': 25, '3': 17, '4': 10, '5': 6, '6': 7, '7': 19, '8': 200, '9': 200, '10': 200, 'A': 200},
    '9,9': {'2': -3, '3': -8, '4': -10, '5': -15, '6': -14, '7': -8, '8': -16, '9': -22, '10': 200, 'A': 10},
    '8,8': {'2': -100, '3': -100, '4': -100, '5': -100, '6': -100, '7': -100, '8': -100, '9': -100, '10': 24, 'A': -18},
    '7,7': {'2': -22, '3': -29, '4': -35, '5': -100, '6': -100, '7': -100, '8': -100, '9': 200, '10': 200, 'A': 200},
    '6,6': {'2': 0, '3': -3, '4': -8, '5': -13, '6': -16, '7': -8, '8': 200, '9': 200, '10': 200, 'A': 200},
    '5,5': {'2': 200, '3': 200, '4': 200, '5': 200, '6': 200, '7': 200, '8': 200, '9': 200, '10': 200, 'A': 200},
    '4,4': {'2': 200, '3': 18, '4': 8, '5': 0, '6': 5, '7': 200, '8': 200, '9': 200, '10': 200, 'A': 200},
    '3,3': {'2': -21, '3': -23, '4': -100, '5': -100, '6': -100, '7': -100, '8': [-2, 6], '9': 200, '10': 200, 'A': 200},
    '2,2': {'2': -9, '3': -15, '4': -22, '5': -30, '6': -100, '7': -100, '8': 200, '9': 200, '10': 200, 'A': 200},
}