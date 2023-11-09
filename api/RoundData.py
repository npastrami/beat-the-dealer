class RoundData:
    def __init__(self):
        self.round_number = 0
        self.player_points = {}
        self.dealer_points = 0
        self.player_busts = {}  
        self.dealer_bust = False  

    def start_new_round(self):
        self.round_number += 1
        self.player_points = {}
        self.dealer_points = 0
        self.player_busts = {}
        self.dealer_bust = False

    def update_points(self, player_name, points):
        self.player_points[player_name] = points
        self.player_busts[player_name] = points > 21  

    def update_dealer_points(self, points):
        self.dealer_points = points
        self.dealer_bust = points > 21  

    def determine_winner(self):
        winners = []
        for player, points in self.player_points.items():
            if points > 21:
                continue  
            if points > self.dealer_points or self.dealer_bust:
                winners.append(player)
        return winners