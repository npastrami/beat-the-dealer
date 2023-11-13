import React, { useState, useEffect } from 'react';
import styles from './styles/Controls.module.css';

type ControlsProps = {
  balance: number,
  gameState: number,
  startEvent: () => Promise<void>,
  betEvent: (amount: number) => Promise<void>,
  hitEvent: () => Promise<void>,
  standEvent: () => Promise<void>,
  nextRoundEvent: () => Promise<void>,
};

const Controls: React.FC<ControlsProps> = ({ balance, gameState, startEvent, betEvent, hitEvent, standEvent, nextRoundEvent }) => {
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

  const getControls = () => {
    switch (gameState) {
      case 0: // Start
        return <button onClick={startEvent} className={styles.button}>Start Game</button>;
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
        return (
          <div className={styles.controlsContainer}>
            <button onClick={hitEvent} className={styles.button}>Hit</button>
            <button onClick={standEvent} className={styles.button}>Stand</button>
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