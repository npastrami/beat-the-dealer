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
                    reshuffle_number INT,
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
            
    def insert_seen_card(self, round_number, reshuffle_number, card):
        cursor = self.connection.cursor()
        try:
            seen_cards_query = """
                INSERT INTO seen_cards (round_number, reshuffle_number, card_suit, card_rank)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(seen_cards_query, (round_number, reshuffle_number, card.suit, card.rank))
            self.connection.commit()
        except psycopg2.DatabaseError as e:
            self.connection.rollback()
            print(f"Error while inserting seen card: {e}")
        finally:
            cursor.close()
            
    def fetch_seen_cards_for_reshuffle(self, reshuffle_number):
        cursor = self.connection.cursor()
        try:
            query = "SELECT card_suit, card_rank FROM seen_cards WHERE reshuffle_number = %s"
            cursor.execute(query, (reshuffle_number,))
            seen_cards = cursor.fetchall()
            self.connection.commit()
            return [{'suit': suit, 'rank': rank} for suit, rank in seen_cards]
        except psycopg2.DatabaseError as e:
            print(f"Error fetching seen cards for reshuffle: {e}")
            raise e
        finally:
            cursor.close()
            
    # def reset_seen_cards(self):
    #     cursor = self.connection.cursor()
    #     try:
    #         cursor.execute("TRUNCATE TABLE seen_cards")
    #         self.connection.commit()
    #     except psycopg2.DatabaseError as e:
    #         self.connection.rollback()
    #         print(f"Error resetting seen cards: {e}")
    #     finally:
    #         cursor.close()

    def increment_reshuffle_number(self, current_round_number):
        cursor = self.connection.cursor()
        try:
            # Update only the rounds that are greater than the current round number
            update_query = """
                UPDATE seen_cards
                SET reshuffle_number = reshuffle_number + 1
                WHERE round_number > %s
            """
            cursor.execute(update_query, (current_round_number,))
            self.connection.commit()
        except psycopg2.DatabaseError as e:
            self.connection.rollback()
            print(f"Error incrementing reshuffle number: {e}")
        finally:
            cursor.close()
            
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
    
    def close(self):
        if self.connection:
            self.connection.close()
            print("Database connection closed")