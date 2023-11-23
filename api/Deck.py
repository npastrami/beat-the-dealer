import random
from Card import Card

class Deck:
    def __init__(self, num_decks=2, stop_card_position=None):
        self.cards = []
        self.num_decks = num_decks
        self.suits = ['♥', '♦', '♣', '♠']
        self.ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.stop_card_position = stop_card_position
        self.cards_dealt = 0
        
        for _ in range(self.num_decks):
            for suit in self.suits:
                for rank in self.ranks:
                    self.cards.append(Card(suit, rank))
    
    def shuffle(self):
        random.shuffle(self.cards)
        
    def set_stop_card_position(self, position):
        self.stop_card_position = position
        self.cards = self.cards[:self.stop_card_position]

    def is_time_to_shuffle(self):
        return self.cards_dealt >= self.stop_card_position
        
    def deal(self):
        self.cards_dealt += 1
        return self.cards.pop()
    
    def reset_count(self):
        self.cards_dealt = 0