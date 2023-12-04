class Hand:
    def __init__(self):
        self.cards = []
        self.has_stood = False

    def add_card(self, card):
        self.cards.append(card)
        
    def is_soft(self):
        # A hand is soft if there is an ace and the total value can be either above or below 21
        has_ace = any(card.rank == 'A' for card in self.cards)
        value_with_ace_as_one = self.calculate_value(ace_as_one=True)
        return has_ace and value_with_ace_as_one + 10 <= 21

    def calculate_value(self, ace_as_one=False):
        value = 0
        num_aces = 0
        
        # Add value for non-ace cards
        for card in self.cards:
            if card.rank == "A":
                num_aces += 1
            else:
                value += card.point_value
        
        # Add value for aces
        for _ in range(num_aces):
            if ace_as_one:
                value += 1
            else:
                # Add 11 if it doesn't bust the hand, otherwise add 1
                value += 11 if value + 11 <= 21 else 1
                
        return value

    def is_busted(self):
        return self.calculate_value() > 21
    
    def can_split(self):
        # A hand can be split if it contains exactly two cards of the same rank
        return len(self.cards) == 2 and self.cards[0].rank == self.cards[1].rank
    
    def get_cards(self):
        return self.cards
    
    def stand(self):
        self.has_stood = True