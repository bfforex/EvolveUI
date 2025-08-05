import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Typography,
  Collapse,
  IconButton,
  Chip,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Psychology as ThinkingIcon,
} from '@mui/icons-material';

interface ThinkingProcessProps {
  isThinking: boolean;
  thinkingContent?: string;
  thinkingDuration?: number;
  onComplete?: () => void;
  showDropdown?: boolean;
}

export const ThinkingProcess: React.FC<ThinkingProcessProps> = ({
  isThinking,
  thinkingContent = '',
  thinkingDuration = 0,
  onComplete,
  showDropdown = true,
}) => {
  const [displayedText, setDisplayedText] = useState('');
  const [isComplete, setIsComplete] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [startTime, setStartTime] = useState<number>(0);
  const [currentDuration, setCurrentDuration] = useState(0);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const animationRef = useRef<NodeJS.Timeout | null>(null);

  // Simulate thinking process text
  const generateThinkingSteps = (content: string) => {
    const steps = [
      'Thinking...',
      'Analyzing your question...',
      'Processing information...',
      'Gathering relevant context...',
    ];

    if (content.includes('RAG')) {
      steps.push('Retrieving from knowledge base...');
    }
    if (content.includes('search')) {
      steps.push('Searching for current information...');
    }
    
    steps.push(
      'Considering different approaches...',
      'Structuring the response...',
      'Finalizing answer...',
      'Finished Thinking'
    );

    return steps;
  };

  // Timer effect
  useEffect(() => {
    if (isThinking && !isComplete) {
      setStartTime(Date.now());
      const timer = setInterval(() => {
        setCurrentDuration(Date.now() - startTime);
      }, 100);
      intervalRef.current = timer;

      return () => {
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
        }
      };
    }
  }, [isThinking, isComplete, startTime]);

  // Streaming text animation effect
  useEffect(() => {
    if (isThinking && !isComplete) {
      setDisplayedText('');
      setIsExpanded(true);
      
      const steps = generateThinkingSteps(thinkingContent);
      let currentStepIndex = 0;
      let currentCharIndex = 0;
      let accumulatedText = '';

      const animateText = () => {
        if (currentStepIndex >= steps.length) {
          setIsComplete(true);
          setIsExpanded(false); // Auto-collapse when finished
          if (onComplete) {
            onComplete();
          }
          return;
        }

        const currentStep = steps[currentStepIndex];
        
        if (currentCharIndex <= currentStep.length) {
          const newText = accumulatedText + currentStep.substring(0, currentCharIndex);
          setDisplayedText(newText);
          currentCharIndex++;
        } else {
          // Move to next step
          accumulatedText += currentStep + '\n';
          currentStepIndex++;
          currentCharIndex = 0;
          
          // Add pause between steps
          setTimeout(() => {
            animateText();
          }, currentStepIndex === steps.length - 1 ? 800 : 400); // Longer pause before "Finished Thinking"
          return;
        }

        // Faster typing for thinking animation
        const delay = currentStep === 'Finished Thinking' ? 80 : 30;
        animationRef.current = setTimeout(animateText, delay);
      };

      // Start animation after a brief delay
      setTimeout(animateText, 200);

      return () => {
        if (animationRef.current) {
          clearTimeout(animationRef.current);
        }
      };
    }
  }, [isThinking, thinkingContent, isComplete, onComplete]);

  // Reset when thinking starts again
  useEffect(() => {
    if (isThinking) {
      setIsComplete(false);
      setCurrentDuration(0);
    } else if (thinkingDuration && thinkingDuration > 0) {
      // If we have a thinking duration but not currently thinking, mark as complete
      setIsComplete(true);
    }
  }, [isThinking, thinkingDuration]);

  // Format duration
  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  const finalDuration = isComplete ? currentDuration : (thinkingDuration || currentDuration);

  // Don't render anything if not thinking and no completed content and no duration
  if (!isThinking && !isComplete && !displayedText && !thinkingDuration) {
    return null;
  }

  return (
    <Box sx={{ mb: 2 }}>
      {/* Show current thinking process */}
      {(isThinking || (isComplete && isExpanded)) && (
        <Collapse in={isThinking || isExpanded}>
          <Box
            sx={{
              p: 2,
              bgcolor: 'rgba(255, 255, 255, 0.03)',
              borderRadius: 1,
              border: '1px solid rgba(255, 255, 255, 0.1)',
              position: 'relative',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <ThinkingIcon 
                sx={{ 
                  color: 'text.secondary', 
                  fontSize: 16,
                  animation: isThinking ? 'pulse 1.5s infinite' : 'none',
                }} 
              />
              <Typography
                variant="caption"
                sx={{
                  color: 'text.secondary',
                  fontWeight: 500,
                  textTransform: 'uppercase',
                  letterSpacing: 0.5,
                }}
              >
                {isThinking ? 'AI Thinking' : 'Thinking Process'}
              </Typography>
              {finalDuration > 0 && (
                <Chip
                  size="small"
                  label={formatDuration(finalDuration)}
                  sx={{
                    height: 18,
                    fontSize: '0.6rem',
                    bgcolor: 'rgba(255, 255, 255, 0.1)',
                    color: 'text.secondary',
                  }}
                />
              )}
            </Box>
            
            <Typography
              variant="body2"
              sx={{
                color: '#b0bec5',
                fontStyle: 'italic',
                fontSize: '0.8rem',
                lineHeight: 1.4,
                whiteSpace: 'pre-line',
                minHeight: isThinking ? '20px' : 'auto',
                fontFamily: 'Monaco, Consolas, "Courier New", monospace',
              }}
            >
              {displayedText}
              {isThinking && (
                <Box
                  component="span"
                  sx={{
                    display: 'inline-block',
                    width: '8px',
                    height: '16px',
                    bgcolor: '#b0bec5',
                    ml: 0.5,
                    animation: 'blink 1s infinite',
                  }}
                />
              )}
            </Typography>
          </Box>
        </Collapse>
      )}

      {/* Show dropdown for completed thinking */}
      {(isComplete || (thinkingDuration && thinkingDuration > 0 && !isThinking)) && showDropdown && !isExpanded && (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <IconButton
            size="small"
            onClick={() => setIsExpanded(!isExpanded)}
            sx={{
              color: 'text.secondary',
              '&:hover': {
                bgcolor: 'rgba(255, 255, 255, 0.05)',
              },
            }}
          >
            {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </IconButton>
          <Typography
            variant="caption"
            sx={{
              color: 'text.secondary',
              cursor: 'pointer',
              '&:hover': {
                color: 'text.primary',
              },
            }}
            onClick={() => setIsExpanded(!isExpanded)}
          >
            Show thinking process ({formatDuration(finalDuration)})
          </Typography>
        </Box>
      )}

      {/* Add CSS keyframes for animations */}
      <style>
        {`
          @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
          }
          @keyframes pulse {
            0% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.1); opacity: 0.7; }
            100% { transform: scale(1); opacity: 1; }
          }
        `}
      </style>
    </Box>
  );
};