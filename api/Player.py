from Hand import Hand

class Player:
    def __init__(self, name, money=1000):
        self.name = name
        self.money = money
        self.hands = [Hand()]
        self.current_bet = 0
        self.has_stood = False
            
    def bet(self, amount):
        if amount > self.money:
            return False
        self.current_bet = amount
        self.money -= amount
        return True
    
    def win(self):
        self.money += 2 * self.current_bet
        
    def add_hand(self):
        new_hand = Hand()
        self.hands.append(new_hand)
        self.current_bet.append(self.current_bet[-1])  # Assuming self.current_bet is a list

    def remove_hand(self, index):
        del self.hands[index]
        del self.current_bet[index]
        
    def reset_for_new_round(self):
        self.hands = [Hand()]
        self.current_bet = 0