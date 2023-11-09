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

    # Log the received parameters
    print("Number of Decks:", num_decks)
    print("Number of Players:", num_players)

    # Initialize the Game object with the provided parameters
    game = Game(num_decks=num_decks, num_players=num_players)
    
    game.start_game()
    
    # Deal initial cards
    game.deal_initial_cards()

    # Log initial game state
    initial_game_state = game.get_game_state()
    print("Initial Game State:", initial_game_state)

    # Return a success response along with the initial game state
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

    game.player_action_stand(player)

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

if __name__ == '__main__':
    app.run(debug=True)