from flask import Flask, request, jsonify
from Game import Game
# main branch for git
app = Flask(__name__)

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

    # Initialize the Game object with the provided parameters
    game = Game(num_decks=num_decks, num_players=num_players)
    
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
        return jsonify({'roundResults': round_results})

    # If the round is not complete, just return the current game state
    print("Round not complete, continuing game.")
    return jsonify(game.get_game_state()) 

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

if __name__ == '__main__':
    app.run(debug=True)