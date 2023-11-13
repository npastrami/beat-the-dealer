import psycopg2

class Database:
    def __init__(self, user_id):
        self.conn_params = {
            "dbname": "BeatTheDealer",
            "user": "postgres",
            "password": "kr3310",
            "host": "localhost",
            "port": "5432"
        }
        self.user_id = user_id
        self.connection = None
        self.connect()
        self.create_tables_if_not_exists()

    def connect(self):
        try:
            self.connection = psycopg2.connect(**self.conn_params)
            print("Database connection established")
        except psycopg2.DatabaseError as e:
            print(f"Error connecting to the database: {e}")
            raise e

    def create_tables_if_not_exists(self):
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rounds (
                    round_number INT,
                    dealer_hand TEXT,
                    running_count INT
                );
                CREATE TABLE IF NOT EXISTS player_hands (
                    round_number INT,
                    player_name TEXT,
                    hand TEXT,
                    bet INT,
                    actions TEXT
                );
                CREATE TABLE IF NOT EXISTS seen_cards (
                    round_number INT,
                    card_suit TEXT,
                    card_rank TEXT
                );
                CREATE TABLE IF NOT EXISTS recommendations (
                    round_number INT,
                    recommended_bet INT,
                    recommended_action TEXT
                );
            """)
            self.connection.commit()
        except psycopg2.DatabaseError as e:
            print(f"Error creating tables: {e}")
            self.connection.rollback()
        finally:
            cursor.close()

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

            # Insert recommendations
            recommendation_query = """
                INSERT INTO recommendations (round_number, recommended_bet, recommended_action)
                VALUES (%s, %s, %s)
            """
            cursor.execute(recommendation_query, (round_data.round_number, round_data.recommended_bet, round_data.recommended_action))

            self.connection.commit()
        except psycopg2.DatabaseError as e:
            self.connection.rollback()
            print(f"Error while inserting round data: {e}")
        finally:
            cursor.close()
            
    def insert_seen_card(self, round_number, card):
        cursor = self.connection.cursor()
        try:
            seen_cards_query = """
                INSERT INTO seen_cards (round_number, card_suit, card_rank)
                VALUES (%s, %s, %s)
            """
            cursor.execute(seen_cards_query, (round_number, card.suit, card.rank))
            self.connection.commit()
        except psycopg2.DatabaseError as e:
            self.connection.rollback()
            print(f"Error while inserting seen card: {e}")
        finally:
            cursor.close()

    def close(self):
        if self.connection:
            self.connection.close()
            print("Database connection closed")
            
    def get_latest_round_data(self, round_number):
        cursor = self.connection.cursor()
        try:
            query = "SELECT * FROM player_hands WHERE round_number = %s"
            cursor.execute(query, (round_number,))
            player_hands = cursor.fetchall()

            # Process and return data as needed for the strategy module
            return player_hands
        except psycopg2.DatabaseError as e:
            print(f"Error fetching round data: {e}")
            raise e
        finally:
            cursor.close()
            