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
                CREATE TABLE IF NOT EXISTS seen_cards (
                    round_number INT,
                    card_suit TEXT,
                    card_rank TEXT
                );
            """)
            self.connection.commit()
        except psycopg2.DatabaseError as e:
            print(f"Error creating tables: {e}")
            self.connection.rollback()
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
            
    def fetch_all_seen_cards(self):
        """
        Fetches all seen cards from the database.
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT card_suit, card_rank FROM seen_cards")
            seen_cards = cursor.fetchall()
            self.connection.commit()
            print("Fetched seen cards from DB:", seen_cards)
            return [{'suit': suit, 'rank': rank} for suit, rank in seen_cards]
        except psycopg2.DatabaseError as e:
            print(f"Error fetching seen cards: {e}")
            raise e
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
            