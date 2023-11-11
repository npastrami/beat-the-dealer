class ThorpStrategy:
    def __init__(self, thorp_count):
        self.thorp_count = thorp_count

    def recommend_move(self, player_hand, dealer_upcard):
        p_value, d_value, p_cards = player_hand.get_value(), dealer_upcard.get_value(), player_hand.cards
        split_cond = lambda r: r in {'A', '8'} or r in {'2', '3', '7', '6', '9'} and d_value < (7 if r != '9' else 10) and d_value != 7

        return ('Split' if len(p_cards) == 2 and p_cards[0].rank == p_cards[1].rank and split_cond(p_cards[0].rank) else
                'Double' if 9 <= p_value <= 11 and (p_value == 9 and 3 <= d_value <= 6 or d_value < (10 if p_value > 9 else 7)) else
                'Stand' if p_value >= 17 or 12 <= p_value <= 16 and d_value < 7 else
                'Hit')