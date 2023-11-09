class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    @property
    def point_value(self):
        if self.rank in ["J", "Q", "K"]:
            return 10
        elif self.rank == "A":
            return 11
        else:
            return int(self.rank)