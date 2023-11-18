import random
from Card import Card

class Deck:
    def __init__(self, num_decks=2):
        self.cards = []
        self.num_decks = num_decks
        self.suits = ['♥', '♦', '♣', '♠']
        self.ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        
        for _ in range(self.num_decks):
            for suit in self.suits:
                for rank in self.ranks:
                    self.cards.append(Card(suit, rank))
    
    def shuffle(self):
        random.shuffle(self.cards)
        
    def deal(self):
        return self.cards.pop()