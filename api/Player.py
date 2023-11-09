from Hand import Hand

class Player:
    def __init__(self, name, money=1000):
        self.name = name
        self.money = money
        self.hands = [Hand()]
        self.bets = [0]  # Make this a list to handle multiple bets for multiple hands
        self.has_stood = False
            
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

    def remove_hand(self, index):
        del self.hands[index]
        del self.bets[index]
        
    def reset_for_new_round(self):
        self.hands = [Hand()]
        self.bets = [0]  # Reset bets for the new round