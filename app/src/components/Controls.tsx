import React, { useState, useEffect } from 'react';
import styles from './styles/Controls.module.css';

type ControlsProps = {
  balance: number,
  gameState: number,
  startEvent: () => Promise<void>,
  betEvent: (amount: number) => Promise<void>,
  hitEvent: () => Promise<void>,
  standEvent: () => Promise<void>,
  doubleDownEvent: () => Promise<void>,
  nextRoundEvent: () => Promise<void>,
  numDecks: number;
  setNumDecks: React.Dispatch<React.SetStateAction<number>>;
  stopCard: number;
  setStopCard: React.Dispatch<React.SetStateAction<number>>;
  reshuffleEvent: () => Promise<void>;
  splitEvent: () => Promise<void>;
};

const Controls: React.FC<ControlsProps> = ({ balance, gameState, startEvent, betEvent, hitEvent, standEvent, nextRoundEvent, numDecks, setNumDecks, stopCard, setStopCard, reshuffleEvent, doubleDownEvent, splitEvent }) => {
  const [amount, setAmount] = useState(10);
  const [inputStyle, setInputStyle] = useState(styles.input);

  useEffect(() => {
    validation();
  }, [amount, balance]);

  const validation = () => {
    if (amount > balance) {
      setInputStyle(styles.inputError);
      return false;
    }
    if (amount < 0.01) {
      setInputStyle(styles.inputError);
      return false;
    }
    setInputStyle(styles.input);
    return true;
  }

  const amountChange = (e: any) => {
    setAmount(e.target.value);
  }

  const onBetClick = () => {
    if (validation()) {
      betEvent(Math.round(amount * 100) / 100);
    }
  }

  const onStartClick = () => {
    if (numDecks >= 1 && numDecks <= 8) { 
      startEvent();
    } else {
      alert("Please enter a valid number of decks (1-8).");
    }
  }

  const getControls = () => {
    switch (gameState) {
      case 0:
        return (
          <div className={styles.startContainer}>
            <div className={styles.inputsContainer}>
              <div className={styles.betContainer}>
                <h4>Number of Decks:</h4>
                <input 
                  type="number" 
                  value={numDecks} 
                  onChange={(e) => setNumDecks(Number(e.target.value))} 
                  className={inputStyle} 
                  min="1" 
                  max="8"
                />
              </div>
              <div className={styles.betContainer}>
                <h4>Stop Card Position (%):</h4>
                <input 
                  type="number" 
                  value={stopCard} 
                  onChange={(e) => setStopCard(Number(e.target.value))} 
                  className={inputStyle} 
                  min="0" 
                  max="100"
                />
              </div>
            </div>
            <button onClick={onStartClick} className={styles.startButton}>Start Game</button>
          </div>
        );
      case 1: // Bet
        return (
          <div className={styles.controlsContainer}>
            <div className={styles.betContainer}>
              <h4>Amount:</h4>
              <input autoFocus type='number' value={amount} onChange={amountChange} className={inputStyle} />
            </div>
            <button onClick={onBetClick} className={styles.button}>Bet</button>
          </div>
        );
      case 2: // Init, User Turn, Dealer Turn
      case 3:
      case 4:
      case 5:
        return (
          <div className={styles.controlsContainer}>
            <button onClick={hitEvent} className={styles.button}>Hit</button>
            <button onClick={standEvent} className={styles.button}>Stand</button>
            <button onClick={doubleDownEvent} className={styles.button}>Double Down</button>
            <button onClick={splitEvent} className={styles.button}>Split</button>
            <button onClick={reshuffleEvent} className={styles.button}>Reshuffle</button>
            <button onClick={nextRoundEvent} className={styles.button}>Next Round</button>
          </div>
        );
      default:
        return null;
    }
  }

  return <>{getControls()}</>;
}

export default Controls;