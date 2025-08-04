import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  IconButton,
  Select,
  MenuItem,
  CircularProgress,
  Avatar,
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
  CloudUpload as UploadIcon,
  Memory as MemoryIcon,
} from '@mui/icons-material';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  thinking?: string; // Optional thinking process content
}

interface Model {
  name: string;
  size?: number;
}

interface ChatPanelProps {
  conversationId: string | null;
  onNewConversation: (id: string) => void;
  showThinkingProcess?: boolean;
  webSearchEnabled?: boolean;
  evolverEnabled?: boolean;
  ragEnabled?: boolean;
  contextLimit?: number;
  onOpenFileUpload?: () => void;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({
  conversationId,
  onNewConversation,
  showThinkingProcess = false,
  webSearchEnabled = true,
  evolverEnabled = false,
  ragEnabled = true,
  contextLimit = 3,
  onOpenFileUpload,
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
        // Simulate thinking process for demonstration when enabled
        const thinking = showThinkingProcess ? 
          `Analyzing your question about "${userMessage.content.substring(0, 30)}..."${userMessage.content.length > 30 ? '...' : ''}\n\nConsidering the context and determining the best approach to provide a helpful response.` 
          : undefined;

        const assistantMessage: Message = {
          role: 'assistant',
          content: data.message.content,
          timestamp: new Date().toISOString(),
          thinking,
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
                {/* Show thinking process if enabled and available */}
                {showThinkingProcess && message.thinking && message.role === 'assistant' && (
                  <Box sx={{ mb: 2, p: 1, bgcolor: 'rgba(255, 255, 255, 0.05)', borderRadius: 1 }}>
                    <Typography
                      variant="caption"
                      sx={{
                        color: 'text.secondary',
                        fontStyle: 'italic',
                        fontSize: '0.75rem',
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word',
                      }}
                    >
                      💭 {message.thinking}
                    </Typography>
                  </Box>
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
      <Box
        sx={{
          p: 2,
          m: 2,
          borderRadius: 2,
        }}
      >
        {/* Phase 2 Features Bar */}
        {(ragEnabled || onOpenFileUpload) && (
          <Box sx={{ 
            display: 'flex', 
            gap: 1, 
            mb: 1, 
            alignItems: 'center',
            justifyContent: 'flex-start'
          }}>
            {ragEnabled && (
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: 0.5,
                bgcolor: 'rgba(25, 118, 210, 0.1)',
                borderRadius: 1,
                px: 1,
                py: 0.5
              }}>
                <MemoryIcon sx={{ fontSize: 14, color: 'primary.main' }} />
                <Typography variant="caption" color="primary.main">
                  RAG Active
                </Typography>
              </Box>
            )}
            {onOpenFileUpload && (
              <IconButton
                size="small"
                onClick={onOpenFileUpload}
                sx={{
                  bgcolor: 'rgba(25, 118, 210, 0.1)',
                  color: 'primary.main',
                  '&:hover': {
                    bgcolor: 'rgba(25, 118, 210, 0.2)',
                  },
                }}
                title="Upload Files"
              >
                <UploadIcon sx={{ fontSize: 16 }} />
              </IconButton>
            )}
          </Box>
        )}
        
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
                bgcolor: 'transparent',
                '& fieldset': {
                  borderColor: 'rgba(255, 255, 255, 0.23)',
                },
                '&:hover fieldset': {
                  borderColor: 'rgba(255, 255, 255, 0.5)',
                },
                '&.Mui-focused fieldset': {
                  borderColor: 'primary.main',
                },
              },
            }}
          />
          <Select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            variant="outlined"
            size="small"
            displayEmpty
            sx={{
              minWidth: 120,
              '& .MuiOutlinedInput-notchedOutline': {
                border: 'none',
              },
              '& .MuiSelect-select': {
                color: 'text.secondary',
                fontSize: '0.875rem',
              },
            }}
          >
            {models.map((model) => (
              <MenuItem key={model.name} value={model.name}>
                {model.name}
              </MenuItem>
            ))}
          </Select>
          <IconButton
            onClick={sendMessage}
            disabled={!inputValue.trim() || isLoading}
            sx={{
              width: 32,
              height: 32,
              color: 'primary.main',
              '&:hover': {
                bgcolor: 'rgba(25, 118, 210, 0.1)',
              },
              '&:disabled': {
                color: 'action.disabled',
              },
            }}
          >
            <SendIcon sx={{ fontSize: 18 }} />
          </IconButton>
        </Box>
      </Box>
    </Box>
  );
};