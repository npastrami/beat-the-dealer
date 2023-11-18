// StrategyDisplay.tsx
import React from 'react';
import './styles/StrategyDisplay.module.css';

interface StrategyDisplayProps {
    suggestion: string;
  }
  
  const StrategyDisplay: React.FC<StrategyDisplayProps> = ({ suggestion }) => {
    return (
      <div style={{ position: 'absolute', bottom: 20, right: 20, backgroundColor: 'black', color: 'white' }}>
        Thorp Action Suggestion: {suggestion}
      </div>
    );
  };
  
  export default StrategyDisplay;