from Player import Player
from Hand import Hand

class Dealer(Player):
    def __init__(self):
        super().__init__("Dealer", money=0)
        
    def should_hit(self):
        print("hit")
        return self.hands[0].calculate_value() < 17 
    
    def reset_for_new_round(self):
        self.hands = [Hand()]