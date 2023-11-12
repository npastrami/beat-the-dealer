class ThorpStrategyBet:
    def __init__(self, base_bet=10):
        self.base_bet = base_bet
        self.running_count = 0

    def update_running_count(self, count):
        self.running_count = count

    def recommend_bet(self):
        # Modify this formula as needed to fit Thorp's strategy
        if self.running_count > 0:
            return self.base_bet * (1 + self.running_count)
        return self.base_bet