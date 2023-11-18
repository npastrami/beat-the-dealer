class ThorpStrategyAction:
    def __init__(self, num_decks=1):
        """
        Initializes the Thorp Strategy Action class.
        """
        self.total_points = 0  
        self.total_unseen_cards = 52 * num_decks  
        self.high_low_index = 0  

    def update_running_count(self, card):
        """
        Updates the running count based on the seen card.
        :param card: The card that has been seen.
        """
        if card.rank in ['2', '3', '4', '5', '6']:
            self.total_points += 1
        elif card.rank in ['10', 'J', 'Q', 'K', 'A']:
            self.total_points -= 1

        # Update total_unseen_cards
        self.total_unseen_cards -= 1
        self.calculate_high_low_index()

    def calculate_high_low_index(self):
        """
        Calculates the high-low index based on current counts.
        """
        if self.total_unseen_cards > 0:
            self.high_low_index = self.total_points / self.total_unseen_cards
        else:
            self.high_low_index = 0

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
        dealer_upcard_value = dealer_upcard.point_value 
        is_soft_hand = player_hand.is_soft()
        can_split = player_hand.can_split()

        # Logic for hard hands using Table 7.1
        if not is_soft_hand and not can_split:
            decision_key = (player_total, dealer_upcard_value)
            if decision_key in hard_hand_decision_dict:
                decision_threshold = hard_hand_decision_dict[decision_key]
                if decision_threshold is not None:
                    if self.high_low_index <= decision_threshold:
                        return 'Hit'
                    else:
                        return 'Stand'
        # Logic for soft hands using Table 7.2
        elif is_soft_hand:
            decision_key = (player_total, dealer_upcard_value)
            if decision_key in soft_hand_decision_dict:
                decision_threshold = soft_hand_decision_dict[decision_key]
                if decision_threshold is not None:
                    if self.high_low_index <= decision_threshold:
                        return 'Hit'
                    else:
                        return 'Stand'
        # Logic for hard doubling down using Table 7.3
        if not is_soft_hand and not can_split and player_total in [9, 10, 11]:
            decision_key = (player_total, dealer_upcard_value)
            if decision_key in hard_double_decision_dict:
                decision_threshold = hard_double_decision_dict[decision_key]
                if decision_threshold is not None:
                    if self.high_low_index > decision_threshold:
                        return 'Double'
                    else:
                        return 'Hit'
        # Logic for soft doubling down using Table 7.4
        if is_soft_hand:
            player_hand_key = 'A,' + str(player_hand.calculate_value() - 11)  # Assuming Ace is always valued at 11 here
            dealer_upcard_key = str(dealer_upcard.point_value)
            
            # Special case for A,6 against dealer's 2
            if player_hand_key == 'A,6' and dealer_upcard_key == '2':
                index_range = soft_double_decision_dict.get((player_hand_key, dealer_upcard_key))
                if self.high_low_index >= index_range[0] and self.high_low_index <= index_range[1]:
                    return 'Double'
            
            # General case for soft doubling down
            decision_threshold = soft_double_decision_dict.get((player_hand_key, dealer_upcard_key))
            if decision_threshold is not None:
                if isinstance(decision_threshold, list):
                    # If the threshold is a list, it means there's a specific range to double down
                    if self.high_low_index > decision_threshold[0] and self.high_low_index < decision_threshold[1]:
                        return 'Double'
                elif self.high_low_index > decision_threshold:
                    return 'Double'
                    
            # Logic for splitting pairs using Table 7.5
            if can_split:
                # Create a key for the decision dictionary based on player's hand and dealer's card
                player_hand_key = ','.join([str(card.rank) for card in player_hand.cards])
                decision_key = (player_hand_key, str(dealer_upcard_value))

                # Check if there's a specific decision for this pair and dealer card
                if decision_key in split_decision_dict:
                    decision_threshold = split_decision_dict[decision_key]

                    # Check for special conditions or a range
                    if isinstance(decision_threshold, list):
                        if decision_threshold[0] < self.high_low_index or self.high_low_index < decision_threshold[1]:
                            return 'Split'
                    elif self.high_low_index > decision_threshold:
                        return 'Split'
                    else:
                        return 'Hit'  # If the high-low index is not high enough to split, choose to hit

            # If no other action is recommended, default to stand
            return 'Stand'

    def adjust_for_seen_card(self, card):
        """
        Adjusts the counts based on a seen card.
        :param card: The card that has been seen.
        """
        self.update_running_count(card)
        
hard_hand_decision_dict = {
    (2, 2): 100, (2, 3): 100, (2, 4): 100, (2, 5): 100, (2, 6): 100, (2, 7): 100, 
    (2, 8): 100, (2, 9): 100, (2, 10): 100, (2, 'A'): 100, (3, 2): 100, (3, 3): 100, 
    (3, 4): 100, (3, 5): 100, (3, 6): 100, (3, 7): 100, (3, 8): 100, (3, 9): 100, 
    (3, 10): 100, (3, 'A'): -15, (4, 2): -21, (4, 3): -25, (4, 4): -30, (4, 5): -34, 
    (4, 6): -35, (4, 7): 10, (4, 8): 11, (4, 9): 6, (4, 10): 2, (4, 'A'): 14, 
    (5, 2): -12, (5, 3): -17, (5, 4): -21, (5, 5): -26, (5, 6): -28, (5, 7): 13, 
    (5, 8): 15, (5, 9): 12, (5, 10): 8, (5, 'A'): 16, (6, 2): -5, (6, 3): -8, 
    (6, 4): -13, (6, 5): -17, (6, 6): -17, (6, 7): 20, (6, 8): 38, (6, 9): None, 
    (6, 10): None, (6, 'A'): None, (7, 2): 1, (7, 3): -2, (7, 4): -5, (7, 5): -9, 
    (7, 6): -8, (7, 7): 50, (7, 8): None, (7, 9): None, (7, 10): None, (7, 'A'): None, 
    (8, 2): 14, (8, 3): 6, (8, 4): 2, (8, 5): -1, (8, 6): 0, (8, 7): None, 
    (8, 8): None, (8, 9): None, (8, 10): None, (8, 'A'): None,
}

soft_hand_decision_dict = {
    # For soft hands of 19 or more, always stand
    (19, '2'): 100, (19, '3'): 100, (19, '4'): 100, (19, '5'): 100,
    (19, '6'): 100, (19, '7'): 100, (19, '8'): 100, (19, '9'): 100,
    (19, '10'): 100, (19, 'A'): 100,
    (20, '2'): 100, 

    # For soft 18
    (18, '2'): 100, (18, '3'): 100, (18, '4'): 100, (18, '5'): 100,
    (18, '6'): 100, (18, '7'): 100, (18, '8'): 100,
    (18, '9'): None, # Draw
    (18, '10'): 12, # Draw if high-low count <= 12
    (18, 'A'): -6,  # Draw if high-low count <= -6

    # For soft 17
    (17, '2'): None, (17, '3'): None, (17, '4'): None, (17, '5'): None,
    (17, '6'): None, (17, '7'): 29,  
    (17, '8'): None, (17, '9'): None, (17, '10'): None, (17, 'A'): None,

    # For soft 16 and below, always draw
    (16, '2'): None, 
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
            ('A,A', '7'): -33, ('A,A', '8'): -24, ('A,A', '9'): -22, ('A,A', '10'): -20, ('A,A', 'A'): -17,
            ('10,10', '2'): 25, ('10,10', '3'): 17, ('10,10', '4'): 10, ('10,10', '5'): 6, ('10,10', '6'): 7, ('10,10', '7'): 19,
            ('9,9', '2'): -3, ('9,9', '3'): -8, ('9,9', '4'): -10, ('9,9', '5'): -15, ('9,9', '6'): -14, ('9,9', '7'): -8, ('9,9', '8'): -16, ('9,9', '9'): -22, ('9,9', 'A'): 10,
            ('8,8', '10'): 24,
            ('7,7', '2'): -22, ('7,7', '3'): -29, ('7,7', '4'): -35,
            ('6,6', '2'): 0, ('6,6', '3'): -3, ('6,6', '4'): -8, ('6,6', '5'): -13, ('6,6', '6'): -16, ('6,6', '7'): -8,
            ('4,4', '6'): 5,
            ('3,3', '8'): [6, -2],
            ('2,2', '2'): -9, ('2,2', '3'): -15, ('2,2', '4'): -22, ('2,2', '5'): -30,
        }