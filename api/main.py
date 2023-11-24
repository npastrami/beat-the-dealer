from flask import Flask, request, jsonify
from Game import Game
# main branch for git
app = Flask(__name__)
game = None

@app.route('/start', methods=['POST'])
def start_game():
    global game

    # Log request payload
    print("Request Payload:", request.json)

    # Get the number of decks and players from the request
    num_decks = int(request.json.get('numDecks', 0))
    num_players = int(request.json.get('numPlayers', 0))
    bet_amount = int(request.json.get('betAmount', 0))  # Retrieve the bet amount from the request

    # Log the received parameters
    print("Number of Decks:", num_decks)
    print("Number of Players:", num_players)
    print("Bet Amount:", bet_amount)

    stop_card_index = int(request.json.get('stopCardIndex', 0))  # Default to 1.0 if not provided
    
    print("Stop card index", stop_card_index)

    # Initialize the Game object with the provided parameters including stop_card_index
    game = Game(num_decks=num_decks, num_players=num_players, stop_card_index=stop_card_index)
    
    # Start the game, which should shuffle the deck
    game.start_game()

    # Place the initial bet for each player
    for player in game.players:
        player.bet(0, bet_amount)  # Assume the bet is always for the first hand at the start

    # Deal initial cards
    game.deal_initial_cards()

    # Get the updated game state which should now include the bets
    initial_game_state = game.get_game_state()
    print("Initial Game State:", initial_game_state)

    # Return a success response along with the updated initial game state
    return jsonify({'message': 'Game started successfully', 'gameState': initial_game_state})

@app.route('/hit', methods=['POST'])
def hit():
    global game
    player_name = request.json.get('player_name')
    print("Player Name:", player_name)

    # Log the current state of the game and players
    print("Current Game State:", game.get_player_hand())

    player = next((p for p in game.players if p.name == player_name), None)
    if not player:
        print("Player not found.")
        return jsonify({'error': 'Player not found'}), 400
    print("Player found:", player)

    game.player_action_hit(player_name)

    return jsonify(game.get_player_hand())


@app.route('/stand', methods=['POST'])
def stand():
    global game
    player_name = request.json.get('player_name')
    player = next((p for p in game.players if p.name == player_name), None)
    if not player:
        return jsonify({'error': 'Player not found'}), 400

    # Mark the player as having stood
    player.has_stood = True
    print(f"{player_name} has stood.")

    # Check if the round is complete
    round_results = game.check_round_completion()

    # If the round is complete, print and return the results
    if round_results is not None:
        for result in round_results:
            print(f"{result['player_name']} {result['result']} against the dealer with hand value {result['player_hand_value']} to dealer's {result['dealer_hand_value']}.")
        print("Round complete, returning results.")
        return jsonify({'roundResults': round_results, 'gameState': game.get_game_state()})  # Include gameState

    # If the round is not complete, just return the current game state
    print("Round not complete, continuing game.")
    current_game_state = game.get_game_state()
    if 'players' not in current_game_state:
        current_game_state['players'] = []  # Ensure players key exists
    return jsonify(current_game_state)

@app.route('/double', methods=['POST'])
def double_down():
    global game
    player_name = request.json.get('player_name')
    player = next((p for p in game.players if p.name == player_name), None)
    if not player:
        return jsonify({'error': 'Player not found'}), 400

    game.player_action_double_down(player)

    return jsonify(game.get_game_state())  

@app.route('/split', methods=['POST'])
def split():
    global game
    player_name = request.json.get('player_name')
    hand_index = request.json.get('hand_index', 0)

    player = next((p for p in game.players if p.name == player_name), None)
    if not player:
        return jsonify({'error': 'Player not found'}), 400

    success = game.player_action_split(player, hand_index)
    if not success:
        return jsonify({'error': 'Cannot split'}), 400

    return jsonify(game.get_game_state())

@app.route('/return_round_results', methods=['POST'])
def return_round_results():
    global game

    try:
        round_results = game.check_round_completion()

        if round_results is not None:
            # Return the results if the round is complete
            return jsonify({'roundResults': round_results})
        else:
            # If the round is not complete, you could return the current state or an indication to continue playing
            return jsonify({'message': 'Round not complete', 'gameState': game.get_game_state()})
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': 'An error occurred while processing round results'}), 500

@app.route('/next_round', methods=['POST'])
def next_round():
    global game

    # Logic to start the next round
    game.prepare_next_round()
    
    game.deal_initial_cards()

    # Fetch the updated game state
    updated_game_state = game.get_game_state()

    return jsonify({'message': 'Next round started successfully', 'gameState': updated_game_state})

@app.route('/bet', methods=['POST'])
def place_bet():
    global game
    player_name = request.json.get('player_name')
    bet_amount = int(request.json.get('betAmount', 0))

    player = next((p for p in game.players if p.name == player_name), None)
    if not player:
        return jsonify({'error': 'Player not found'}), 400

    player.bet(0, bet_amount)  # Update the bet for the player

    return jsonify({'message': 'Bet placed successfully', 'gameState': game.get_game_state()})

@app.route('/thorp_action', methods=['GET'])
def thorp_action():
    global game
    if game:
        suggestion = game.get_last_recommendation()
        print(f"The suggestion: {suggestion}")
        return jsonify({'suggestion': suggestion}), 200
    return jsonify({'error': 'Game not initialized'}), 400

@app.route('/reshuffle', methods=['POST'])
def reshuffle_deck():
    global game
    new_stop_card_position = int(request.json.get('newStopCardPosition', 50)) # Default value

    # Reshuffle the deck and update the stop card position
    game.reshuffle_deck(new_stop_card_position)

    # Return the updated game state
    return jsonify({'message': 'Deck reshuffled successfully', 'gameState': game.get_game_state()})

if __name__ == '__main__':
    app.run(debug=True)
    