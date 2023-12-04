from Hand import Hand

class Player:
    def __init__(self, name, money=1000):
        self.name = name
        self.money = money
        self.hands = [Hand()]
        self.bets = [0]  # Make this a list to handle multiple bets for multiple hands
        self.active_hand_index = 0
            
    def bet(self, hand_index, amount):
        if amount > self.money:
            return False
        self.bets[hand_index] = amount
        self.money -= amount
        return True
    
    def win(self, hand_index):
        self.money += 2 * self.bets[hand_index]
        self.bets[hand_index] = 0  # Reset the bet after a win
        
    def add_hand(self):
        new_hand = Hand()
        self.hands.append(new_hand)
        self.bets.append(self.bets[-1])  # Duplicate the bet for the new hand
    
    # Add method to advance to the next hand
    def next_hand(self):
        if self.active_hand_index < len(self.hands) - 1:
            self.active_hand_index += 1
        # else:
        #     self.active_hand_index = 0  # Reset for the next round
        #     self.has_stood = True  # Mark the player as having stood
    
    def has_more_hands(self):
        return self.active_hand_index < len(self.hands) - 1
    
    def all_hands_stood_or_busted(self):
        return all(hand.has_stood or hand.is_busted() for hand in self.hands)

    def remove_hand(self, index):
        del self.hands[index]
        del self.bets[index]
        
    def reset_for_new_round(self):
        self.hands = [Hand()]
        self.bets = [0]  # Reset bets for the new round
        self.active_hand_index = 0
        
    # def place_bet_for_split(self, original_hand_index):
    #     """
    #     Places a bet for a new hand created by a split,
    #     equal to the bet of the original hand.
    #     """
    #     if original_hand_index < len(self.bets):
    #         bet_amount = self.bets[original_hand_index]
    #         if bet_amount > self.money:
    #             return False  # Not enough money to place the bet
    #         self.bets.append(bet_amount)
    #         self.money -= bet_amount
    #         return True
    #     return False