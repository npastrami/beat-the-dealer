import psycopg2

class Database:
    def __init__(self, user_id):
        self.conn = psycopg2.connect(
            dbname="Beat-The-Dealer",
            user="postgres",
            password="BigDeezNutz",
            host="localhost",
            port="5432"
        )
        self.user_id = user_id

    def connect(self):
        try:
            self.connection = psycopg2.connect(**self.user_ids)
            print("Database connection established")
        except psycopg2.DatabaseError as e:
            print(f"Error connecting to the database: {e}")
            raise e

    def close(self):
        if self.connection:
            self.connection.close()
            print("Database connection closed")

    def insert_round_data(self, round_data):
        cursor = self.connection.cursor()
        try:
            # Insert round data
            round_query = """
                INSERT INTO rounds (round_number, dealer_hand, running_count)
                VALUES (%s, %s, %s)
            """
            dealer_hand = ','.join(f"{card.rank}{card.suit}" for card in round_data.dealer_hand)
            cursor.execute(round_query, (round_data.round_number, dealer_hand, round_data.running_count))

            # Insert player data
            for player_name, hand in round_data.player_hands.items():
                player_hand = ','.join(f"{card.rank}{card.suit}" for card in hand)
                player_query = """
                    INSERT INTO player_hands (round_number, player_name, hand, bet, actions)
                    VALUES (%s, %s, %s, %s, %s)
                """
                actions = ','.join(round_data.player_actions.get(player_name, []))
                cursor.execute(player_query, (round_data.round_number, player_name, player_hand, round_data.player_bets.get(player_name, 0), actions))

            self.connection.commit()
        except psycopg2.DatabaseError as e:
            self.connection.rollback()
            print(f"Error while inserting round data: {e}")
            raise e
        finally:
            cursor.close()