import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  IconButton,
  Avatar,
  Button,
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
} from '@mui/icons-material';
import { ThinkingProcess } from './ThinkingProcess';

interface DemoMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  thinking?: string;
  thinkingDuration?: number;
}

export const ThinkingDemo: React.FC = () => {
  const [messages, setMessages] = useState<DemoMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const [currentThinkingIndex, setCurrentThinkingIndex] = useState<number | null>(null);

  const sendDemoMessage = async () => {
    if (!inputValue.trim() || isThinking) return;

    const userMessage: DemoMessage = {
      role: 'user',
      content: inputValue,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsThinking(true);
    setCurrentThinkingIndex(messages.length + 1);

    // Simulate thinking duration
    const thinkingStartTime = Date.now();
    
    // Simulate AI response after thinking
    setTimeout(() => {
      const thinkingDuration = Date.now() - thinkingStartTime;
      
      const assistantMessage: DemoMessage = {
        role: 'assistant',
        content: `I've thought carefully about your question: "${userMessage.content}". This is a fascinating topic that requires deep analysis. Let me provide you with a comprehensive answer based on my understanding and the context I've gathered.`,
        timestamp: new Date().toISOString(),
        thinking: `Analyzing your question about "${userMessage.content.substring(0, 30)}..."${userMessage.content.length > 30 ? '...' : ''}\n\n🧠 Retrieved relevant context from knowledge base\n\n🔍 Searched for up-to-date information\n\n📚 Using multiple sources to enhance my response\n\nDetermining the best approach to provide a comprehensive and helpful response.`,
        thinkingDuration,
      };

      setMessages(prev => [...prev, assistantMessage]);
      setIsThinking(false);
      setCurrentThinkingIndex(null);
    }, 3000); // 3 second thinking simulation
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendDemoMessage();
    }
  };

  return (
    <Box
      sx={{
        maxWidth: 800,
        mx: 'auto',
        p: 3,
        bgcolor: 'background.default',
        minHeight: '100vh',
      }}
    >
      <Typography variant="h4" sx={{ mb: 3, textAlign: 'center' }}>
        AI Thinking Process Demo
      </Typography>
      
      <Typography variant="body1" sx={{ mb: 3, color: 'text.secondary', textAlign: 'center' }}>
        This demo shows the AI thinking process feature with streaming animation, 
        timing display, and collapsible thinking history.
      </Typography>

      {/* Messages Area */}
      <Box
        sx={{
          minHeight: 400,
          maxHeight: 600,
          overflow: 'auto',
          p: 2,
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: 2,
          mb: 3,
          display: 'flex',
          flexDirection: 'column',
          gap: 2,
        }}
      >
        {messages.length === 0 ? (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
              textAlign: 'center',
              color: 'text.secondary',
            }}
          >
            <BotIcon sx={{ fontSize: 64, mb: 2, opacity: 0.5 }} />
            <Typography variant="h6" gutterBottom>
              Start a conversation to see the thinking process
            </Typography>
          </Box>
        ) : (
          messages.map((message, index) => (
            <Box
              key={index}
              sx={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: 2,
                maxWidth: '100%',
              }}
            >
              <Avatar
                sx={{
                  bgcolor: message.role === 'user' ? 'primary.main' : 'secondary.main',
                  width: 32,
                  height: 32,
                }}
              >
                {message.role === 'user' ? <PersonIcon /> : <BotIcon />}
              </Avatar>
              <Paper
                elevation={1}
                sx={{
                  p: 2,
                  flex: 1,
                  bgcolor: message.role === 'user' ? 'primary.dark' : 'background.paper',
                  maxWidth: '80%',
                }}
              >
                {/* Show thinking process for assistant messages */}
                {message.role === 'assistant' && (
                  <ThinkingProcess
                    isThinking={currentThinkingIndex === index}
                    thinkingContent={message.thinking || ''}
                    thinkingDuration={message.thinkingDuration}
                    showDropdown={true}
                  />
                )}
                
                <Typography
                  variant="body1"
                  sx={{
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                  }}
                >
                  {message.content}
                </Typography>
              </Paper>
            </Box>
          ))
        )}
        
        {/* Show current thinking process */}
        {isThinking && (
          <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
            <Avatar sx={{ bgcolor: 'secondary.main', width: 32, height: 32 }}>
              <BotIcon />
            </Avatar>
            <Paper elevation={1} sx={{ p: 2, bgcolor: 'background.paper', flex: 1, maxWidth: '80%' }}>
              <ThinkingProcess
                isThinking={true}
                thinkingContent="Analyzing your question..."
                showDropdown={false}
              />
            </Paper>
          </Box>
        )}
      </Box>

      {/* Input Area */}
      <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-end' }}>
        <TextField
          fullWidth
          multiline
          maxRows={4}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask me anything to see the thinking process..."
          variant="outlined"
          disabled={isThinking}
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: 2,
            },
          }}
        />
        <IconButton
          onClick={sendDemoMessage}
          disabled={!inputValue.trim() || isThinking}
          sx={{
            width: 48,
            height: 48,
            color: 'primary.main',
            '&:hover': {
              bgcolor: 'rgba(25, 118, 210, 0.1)',
            },
          }}
        >
          <SendIcon />
        </IconButton>
      </Box>

      <Box sx={{ mt: 3, textAlign: 'center' }}>
        <Button 
          variant="outlined" 
          onClick={() => {
            setMessages([]);
            setIsThinking(false);
            setCurrentThinkingIndex(null);
          }}
          sx={{ mr: 2 }}
        >
          Clear Demo
        </Button>
        <Typography variant="caption" sx={{ color: 'text.secondary', display: 'block', mt: 1 }}>
          This is a demo of the thinking process feature. The actual AI responses will vary.
        </Typography>
      </Box>
    </Box>
  );
};