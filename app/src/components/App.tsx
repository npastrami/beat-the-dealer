import React, { useState, useEffect } from 'react';
import StrategyDisplay from './StrategyDisplay';
import Status from './Status';
import Controls from './Controls';
import Hand from './Hand';

type CardType = {
  suit: string;
  value: string;
  hidden?: boolean;
};

type CardTuple = [string, string];

const App: React.FC = () => {
  enum GameState {
    start,
    bet,
    init,
    userTurn,
    dealerTurn,
    roundOver
  }

  enum Message {
    start = 'Press Start to Play!',
    bet = 'Place a Bet!',
    hitStand = 'Hit or Stand?',
    bust = 'Bust!',
    userWin = 'Player1 Win!',
    dealerWin = 'Dealer Wins!',
    tie = 'Tie!'
  }

  const [userCards, setUserCards]: any[] = useState([]);
  const [userScore, setUserScore] = useState(0);
  const [dealerCards, setDealerCards]: any[] = useState([]);
  const [dealerScore, setDealerScore] = useState(0);
  const [balance, setBalance] = useState(1000);
  const [bet, setBet] = useState(0);
  const [gameState, setGameState] = useState(GameState.start);
  const [message, setMessage] = useState(Message.start);
  const [thorpSuggestion, setThorpSuggestion] = useState('');
  const [numDecks, setNumDecks] = useState(1);
  const [stopCard, setStopCard] = useState(50);
  const [userSplitCards, setUserSplitCards] = useState([]);
  const [userSplitScore, setUserSplitScore] = useState(0);
  const [activeHandIndex, setActiveHandIndex] = useState(0);

  const [buttonState, setButtonState] = useState({
    hitDisabled: false,
    standDisabled: false,
    resetDisabled: true
  });

  const resetGame = () => {
    console.clear();
    setUserCards([]);
    setUserScore(0);
    setDealerCards([]);
    setDealerScore(0);
    setBet(0);
    setGameState(GameState.bet);
    setMessage(Message.bet);
    setButtonState({
      hitDisabled: false,
      standDisabled: false,
      resetDisabled: true
    });
  };

  const startGame = async () => {
    try {
      const response = await fetch("/start", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        // If your backend expects specific data, include it here
        // For example, if it needs the number of players or decks, you could send it like this:
        body: JSON.stringify({
          numDecks: numDecks,
          numPlayers: 1,
          stopCardIndex: stopCard,
        })
      });
  
      if (response.ok) {
        const data = await response.json();
        // Handle the response data as needed
        setGameState(GameState.bet);
        setMessage(Message.bet);
      } else {
        console.error("Failed to start game");
      }
    } catch (error) {
      console.error("An error occurred:", error);
    }
  };

  const placeBet = async (amount: number) => {
    try {
      const response = await fetch("/bet", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ player_name: "Player 1", betAmount: amount })
      });
      if (response.ok) {
        const data = await response.json();
        updateGameState(data.gameState);
        setBet(amount);
        setGameState(GameState.userTurn);
        fetchThorpSuggestion();
      } else {
        console.error("Failed to place bet");
      }
    } catch (error) {
      console.error("An error occurred:", error);
    }
  };

  const updateGameState = (data: any) => {
    if (data && data.players && data.players.length > 0) {
      // Assuming that each player has at least one hand with cards
      const playerData = data.players[0];
      setUserCards(playerData.hands[0].cards.map((card: [string, string]) => ({
        suit: card[0],
        value: card[1],
        hidden: false
      } as CardType)));

      if (playerData.hands.length > 1) {
        // Handle split hand scenario
        setUserSplitCards(playerData.hands[1].cards.map((card: [string, string]) => ({
          suit: card[0],
          value: card[1],
          hidden: false
        } as CardType)));
      }

      setUserScore(playerData.hands[0].hand_value);
      setBalance(playerData.chips);
    }
    if (data && data.dealer && data.dealer.hand) {
      setDealerCards(data.dealer.hand.map((card: [string, string]) => ({ suit: card[0], value: card[1], hidden: false })));
      setDealerScore(data.dealer.hand_value);
    }
  };

  const hit = async () => {
    try {
      const response = await fetch("/hit", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          player_name: "Player 1", hand_index: activeHandIndex
        }),
      });
  
      const data = await response.json();
      const playerHand = data.players.find((player: { name: string; }) => player.name === "Player 1");
      if (activeHandIndex === 0) {
        setUserCards(playerHand.hands[0].cards.map((card: CardTuple) => ({ suit: card[0], value: card[1], hidden: false })));
        setUserScore(playerHand.hands[0].hand_value);
      } else if (activeHandIndex === 1 && playerHand.hands.length > 1) {
        setUserSplitCards(playerHand.hands[1].cards.map((card: CardTuple) => ({ suit: card[0], value: card[1], hidden: false })));
        setUserSplitScore(playerHand.hands[1].hand_value);
      }
      setBalance(playerHand.chips || balance);
      fetchThorpSuggestion();
    } catch (error) {
      console.error("Error hitting:", error);
    }
  };

  const stand = async () => {
    try {
      const response = await fetch("/stand", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          player_name: "Player 1", hand_index: activeHandIndex
        }),
      });
  
      const data = await response.json();
      updateGameState(data.gameState);
      if (data.roundResults) {
        // Round results are present, indicating the end of the round
        const result = data.roundResults[data.roundResults.length - 1];
        setUserScore(result.player_hand_value);
        setDealerScore(result.dealer_hand_value);
        setMessage(result.result === "win" ? Message.userWin : result.result === "lose" ? Message.dealerWin : Message.tie);
        setButtonState({
          hitDisabled: true,
          standDisabled: true,
          resetDisabled: false
        });
        setGameState(GameState.userTurn);
        updateGameState(data.gameState);
      } else {
        // No round results, so check if there are more hands to play
        const playerData = data.players.find((player: { name: string; }) => player.name === "Player 1");
        if (playerData && playerData.hands.length > activeHandIndex + 1) {
          // Move to the next hand
          setActiveHandIndex(activeHandIndex + 1);
        } else {
          // No more hands to play; move to the dealer's turn
          setGameState(GameState.roundOver);
        }
        updateGameState(data);
      }
    } catch (error) {
      console.error("Error standing:", error);
    }
  };

  const doubleDown = async () => {
    try {
      const response = await fetch("/double", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          player_name: "Player 1",
        }),
      });
  
      const data = await response.json();
      updateGameState(data.gameState);
      fetchThorpSuggestion();
    } catch (error) {
      console.error("Error during double down:", error);
    }
  };

  const split = async () => {
    try {
      const response = await fetch("/split", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          player_name: "Player 1",
          hand_index: 0 // Assuming the first hand is being split
        }),
      });
  
      if (response.ok) {
        const data = await response.json();
        // Update state for both original and split hands
        setUserCards(data.players[0].hands[0].cards.map((card: CardTuple) => ({ suit: card[0], value: card[1], hidden: false })));
        setUserSplitCards(data.players[0].hands[1].cards.map((card: CardTuple) => ({ suit: card[0], value: card[1], hidden: false })));
        // Update scores for both hands
        setUserScore(data.players[0].hands[0].hand_value);
        setUserSplitScore(data.players[0].hands[1].hand_value);
      } else {
        console.error("Failed to split hand");
      }
    } catch (error) {
      console.error("Error splitting hand:", error);
    }
  };

  const nextRound = async () => {
    try {
      const response = await fetch("/next_round", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
  
      if (response.ok) {
        // Clear current cards and scores
        setUserCards([]);
        setUserScore(0);
        setUserSplitCards([]);
        setUserSplitScore(0);
        setActiveHandIndex(0);
        setDealerCards([]);
        setDealerScore(0);
  
        // Transition to betting phase for the new round
        setGameState(GameState.bet);
        setMessage(Message.bet);
        setButtonState({
          hitDisabled: false,
          standDisabled: false,
          resetDisabled: true
        });
      } else {
        console.error("Failed to start the next round");
      }
    } catch (error) {
      console.error("An error occurred while starting the next round:", error);
    }
  };

  const fetchThorpSuggestion = async () => {
    try {
      const response = await fetch('/thorp_action');
      if (response.ok) {
        const { suggestion } = await response.json();
        setThorpSuggestion(suggestion);
      } else {
        console.error("Failed to fetch Thorp suggestion");
      }
    } catch (error) {
      console.error("Error fetching Thorp Suggestion:", error);
    }
  };

  useEffect(() => {
    // Call fetchThorpSuggestion every time the gameState changes
    fetchThorpSuggestion();
  }, [gameState]);

  const reshuffle = async () => {
    const newStopCardPosition = prompt("Enter new stop card position (%):", "50");
    if (newStopCardPosition !== null) {
      try {
        const response = await fetch('/reshuffle', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ newStopCardPosition: parseInt(newStopCardPosition) })
        });
        if (response.ok) {
          const data = await response.json();
          updateGameState(data.gameState);
          // Optional: reset other states if necessary
        } else {
          console.error('Failed to reshuffle');
        }
      } catch (error) {
        console.error('Error during reshuffle:', error);
      }
    }
  };

  // const bust = () => {
  //   buttonState.hitDisabled = true;
  //   buttonState.standDisabled = true;
  //   buttonState.resetDisabled = false;
  //   setButtonState({ ...buttonState });
  //   setMessage(Message.bust);
  // }

  // const checkWin = () => {
  //   if (userScore > dealerScore || dealerScore > 21) {
  //     setBalance(Math.round((balance + (bet * 2)) * 100) / 100);
  //     setMessage(Message.userWin);
  //   }
  //   else if (dealerScore > userScore) {
  //     setMessage(Message.dealerWin);
  //   }
  //   else {
  //     setBalance(Math.round((balance + (bet * 1)) * 100) / 100);
  //     setMessage(Message.tie);
  //   }
  // }

  return (
    <>
      <Status message={message} balance={balance} />
      <Controls
        balance={balance}
        gameState={gameState}
        startEvent={startGame}
        betEvent={placeBet}
        hitEvent={hit}
        standEvent={stand}
        nextRoundEvent={nextRound}
        numDecks={numDecks}
        setNumDecks={setNumDecks}
        stopCard={stopCard}
        setStopCard={setStopCard}
        reshuffleEvent={reshuffle}
        doubleDownEvent={doubleDown}
        splitEvent={split}
      />
      <StrategyDisplay suggestion={thorpSuggestion} />
      <Hand title={`Dealer's Hand (${dealerScore})`} cards={dealerCards} />
      <div style={{ display: 'flex' }}>
        <Hand 
          title={`Your Hand (${userScore})`} 
          cards={userCards} 
          style={activeHandIndex === 0 ? { textDecoration: 'underline' } : {}} 
        />
        {userSplitCards.length > 0 && (
          <Hand 
            title={`Your Split Hand (${userSplitScore})`} 
            cards={userSplitCards} 
            style={activeHandIndex === 1 ? { textDecoration: 'underline' } : {}} 
          />
        )}
      </div>
    </>
  );
}

export default App;