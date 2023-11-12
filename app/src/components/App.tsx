import React, { useState } from 'react';  // Removed useEffect
import Status from './Status';
import Controls from './Controls';
import Hand from './Hand';

const App: React.FC = () => {
  enum GameState {
    bet,
    init,
    userTurn,
    dealerTurn
  }

  enum Message {
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

  const [gameState, setGameState] = useState(GameState.bet);
  const [message, setMessage] = useState(Message.bet);

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

  const placeBet = async (amount: number) => {
    try {
      const response = await fetch("/start", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          numDecks: 1,
          numPlayers: 1,
          betAmount: amount,
        }),
      });
  
      if (response.ok) {
        const data = await response.json();
        const playersData = data?.gameState?.players;
        const dealerData = data?.gameState?.dealer;

        console.log(data);
  
        if (playersData && playersData.length > 0 && playersData[0].hands && playersData[0].hands[0].cards) {
          setUserCards(playersData[0].hands[0].cards.map((card: [string, string]) => ({ suit: card[0], value: card[1], hidden: false })));
          setUserScore(playersData[0].hands[0].hand_value);
          setBalance(playersData[0].chips);
        } else {
          console.error("Unexpected gameState structure for players", playersData);
          return;
        }
  
        if (dealerData && dealerData.hand) {
          setDealerCards(dealerData.hand.map((card: [string, string]) => ({ suit: card[0], value: card[1], hidden: false })));
          setDealerScore(dealerData.hand_value);
        } else {
          console.error("Unexpected gameState structure for dealer", dealerData);
          return;
        }

        console.log("Set userCards to:", playersData[0].hands[0].cards);  // Log the set value of userCards
        console.log("Set dealerCards to:", dealerData.hand);  // Log the set value of dealerCards
  
        setBet(amount);
        setGameState(GameState.init);
      } else {
        console.error("Failed to start game");
      }
    } catch (error) {
      console.error("An error occurred:", error);
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
          player_name: "Player 1",
        }),
      });

      const data = await response.json();
      const playerHand = data.players.find((player: { name: string; }) => player.name === "Player 1")
      console.log(playerHand.hands[0].cards.map((card: [string, string]) => ({ suit: card[0], value: card[1], hidden: false })))
      setUserCards(playerHand.hands[0].cards.map((card: [string, string]) => ({ suit: card[0], value: card[1], hidden: false })))
      setUserScore(playerHand.hands[0].hand_value)
      setBalance(playerHand.balance);
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
          player_name: "Player 1",
        }),
      });
  
      const data = await response.json();
      if (data.roundResults) {
        const result = data.roundResults[0];
        setUserScore(result.player_hand_value);
        setDealerScore(result.dealer_hand_value);
        setMessage(result.result === "win" ? Message.userWin : result.result === "lose" ? Message.dealerWin : Message.tie);
        setButtonState({
          ...buttonState,
          hitDisabled: true,
          standDisabled: true,
          resetDisabled: false
        });
        setGameState(GameState.dealerTurn);
        setBalance((data.players || []).find((player: { name: string; }) => player.name === "Player 1")?.balance || balance);
      }
    } catch (error) {
      console.error("Error standing:", error);
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
        buttonState={buttonState}
        betEvent={placeBet}
        hitEvent={hit}
        standEvent={stand}
        resetEvent={resetGame}
        nextRoundEvent={nextRound}
      />
      <Hand title={`Dealer's Hand (${dealerScore})`} cards={dealerCards} />
      <Hand title={`Your Hand (${userScore})`} cards={userCards} />
    </>
  );
}

export default App;