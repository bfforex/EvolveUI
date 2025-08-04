import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  IconButton,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  Avatar,
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
} from '@mui/icons-material';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface Model {
  name: string;
  size?: number;
}

interface ChatPanelProps {
  conversationId: string | null;
  onNewConversation: (id: string) => void;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({
  conversationId,
  onNewConversation,
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [models, setModels] = useState<Model[]>([]);
  const [selectedModel, setSelectedModel] = useState('llama3.2');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load available models
  useEffect(() => {
    fetchModels();
  }, []);

  // Load conversation messages when conversation changes
  useEffect(() => {
    if (conversationId) {
      fetchConversationMessages(conversationId);
    } else {
      setMessages([]);
    }
  }, [conversationId]);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchModels = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/models/');
      const data = await response.json();
      if (data.models && data.models.length > 0) {
        setModels(data.models);
        if (data.models[0].name) {
          setSelectedModel(data.models[0].name);
        }
      }
    } catch (error) {
      console.error('Failed to fetch models:', error);
      // Set default models if Ollama is not available
      setModels([
        { name: 'llama3.2' },
        { name: 'llama3.1' },
        { name: 'codellama' },
      ]);
    }
  };

  const fetchConversationMessages = async (convId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/conversations/${convId}`);
      const data = await response.json();
      if (data.conversation) {
        setMessages(data.conversation.messages || []);
      }
    } catch (error) {
      console.error('Failed to fetch conversation messages:', error);
    }
  };

  const createNewConversation = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/conversations/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: 'New Conversation'
        }),
      });
      const data = await response.json();
      if (data.conversation) {
        return data.conversation.id;
      }
    } catch (error) {
      console.error('Failed to create conversation:', error);
    }
    return null;
  };

  const addMessageToConversation = async (convId: string, role: string, content: string) => {
    try {
      await fetch(`http://localhost:8000/api/conversations/${convId}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          role,
          content,
        }),
      });
    } catch (error) {
      console.error('Failed to add message to conversation:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      role: 'user',
      content: inputValue,
      timestamp: new Date().toISOString(),
    };

    let currentConversationId = conversationId;

    // Create new conversation if none selected
    if (!currentConversationId) {
      currentConversationId = await createNewConversation();
      if (currentConversationId) {
        onNewConversation(currentConversationId);
      }
    }

    // Add user message
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    // Save user message to backend
    if (currentConversationId) {
      await addMessageToConversation(currentConversationId, 'user', userMessage.content);
    }

    try {
      // Send to Ollama
      const response = await fetch('http://localhost:8000/api/models/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: selectedModel,
          messages: [...messages, userMessage].map(msg => ({
            role: msg.role,
            content: msg.content,
          })),
        }),
      });

      const data = await response.json();
      
      if (data.message) {
        const assistantMessage: Message = {
          role: 'assistant',
          content: data.message.content,
          timestamp: new Date().toISOString(),
        };

        setMessages(prev => [...prev, assistantMessage]);

        // Save assistant message to backend
        if (currentConversationId) {
          await addMessageToConversation(currentConversationId, 'assistant', assistantMessage.content);
        }
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please make sure Ollama is running and try again.',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  return (
    <Box
      sx={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        bgcolor: 'background.default',
      }}
    >
      {/* Messages Area */}
      <Box
        sx={{
          flex: 1,
          overflow: 'auto',
          p: 2,
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
            <Typography variant="h5" gutterBottom>
              Welcome to EvolveUI
            </Typography>
            <Typography variant="body1">
              Start a conversation with your AI assistant
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
        {isLoading && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar sx={{ bgcolor: 'secondary.main', width: 32, height: 32 }}>
              <BotIcon />
            </Avatar>
            <Paper elevation={1} sx={{ p: 2, bgcolor: 'background.paper' }}>
              <CircularProgress size={20} />
            </Paper>
          </Box>
        )}
        <div ref={messagesEndRef} />
      </Box>

      {/* Input Area */}
      <Paper
        elevation={2}
        sx={{
          p: 2,
          m: 2,
          bgcolor: 'background.paper',
          borderRadius: 2,
        }}
      >
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-end' }}>
          <TextField
            fullWidth
            multiline
            maxRows={4}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            variant="outlined"
            disabled={isLoading}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 2,
              },
            }}
          />
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Model</InputLabel>
            <Select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              label="Model"
            >
              {models.map((model) => (
                <MenuItem key={model.name} value={model.name}>
                  {model.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <IconButton
            onClick={sendMessage}
            disabled={!inputValue.trim() || isLoading}
            color="primary"
            sx={{
              bgcolor: 'primary.main',
              color: 'white',
              '&:hover': {
                bgcolor: 'primary.dark',
              },
              '&:disabled': {
                bgcolor: 'action.disabled',
              },
            }}
          >
            <SendIcon />
          </IconButton>
        </Box>
      </Paper>
    </Box>
  );
};