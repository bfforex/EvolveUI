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
  Chip,
  Collapse,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Link,
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
  Search as SearchIcon,
  Storage as StorageIcon,
  Chat as ConversationIcon,
  OpenInNew as OpenInNewIcon,
} from '@mui/icons-material';
import { ThinkingProcess } from './ThinkingProcess';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  thinking?: string; // Optional thinking process content
  thinkingDuration?: number; // Duration of thinking process in milliseconds
  context_sources?: Array<{
    type: 'knowledge' | 'conversation' | 'web_search';
    title?: string;
    url?: string;
    snippet?: string;
    metadata?: any;
    relevance?: number;
  }>;
  rag_used?: boolean;
  search_used?: boolean;
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
  settings?: any;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({
  conversationId,
  onNewConversation,
  showThinkingProcess = true, // Default to true for demo
  webSearchEnabled = true,
  evolverEnabled = false,
  ragEnabled = true,
  settings = {},
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [models, setModels] = useState<Model[]>([]);
  const [selectedModel, setSelectedModel] = useState('llama3.2');
  const [showContextSources, setShowContextSources] = useState<{ [key: number]: boolean }>({});
  const [currentThinking, setCurrentThinking] = useState<{
    messageIndex: number;
    startTime: number;
    content: string;
  } | null>(null);
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

    // Start thinking process if enabled
    const messageIndex = messages.length; // Assistant message will be at this index
    const thinkingStartTime = Date.now();
    
    if (showThinkingProcess) {
      setCurrentThinking({
        messageIndex,
        startTime: thinkingStartTime,
        content: `Analyzing your question about "${userMessage.content.substring(0, 30)}..."${userMessage.content.length > 30 ? '...' : ''}`,
      });
    }

    // Save user message to backend
    if (currentConversationId) {
      await addMessageToConversation(currentConversationId, 'user', userMessage.content);
    }

    try {
      // Send to Ollama with RAG and search features
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
          use_rag: ragEnabled,
          auto_search: webSearchEnabled,
          conversation_id: currentConversationId || 'default',
        }),
      });

      const data = await response.json();
      
      if (data.message) {
        const thinkingEndTime = Date.now();
        const thinkingDuration = thinkingEndTime - thinkingStartTime;

        // Enhanced thinking process that considers RAG and search
        let thinkingText = '';
        if (showThinkingProcess) {
          thinkingText = `Analyzing your question about "${userMessage.content.substring(0, 30)}..."${userMessage.content.length > 30 ? '...' : ''}`;
          
          if (data.rag_used) {
            thinkingText += '\n\n🧠 Retrieved relevant context from knowledge base';
          }
          
          if (data.search_used) {
            thinkingText += '\n\n🔍 Searched the web for up-to-date information';
          }
          
          if (data.context_sources && data.context_sources.length > 0) {
            thinkingText += `\n\n📚 Using ${data.context_sources.length} source(s) to enhance my response`;
          }
          
          thinkingText += '\n\nDetermining the best approach to provide a comprehensive and helpful response.';
        }

        const assistantMessage: Message = {
          role: 'assistant',
          content: data.message.content,
          timestamp: new Date().toISOString(),
          thinking: thinkingText || undefined,
          thinkingDuration: showThinkingProcess ? thinkingDuration : undefined,
          context_sources: data.context_sources || [],
          rag_used: data.rag_used || false,
          search_used: data.search_used || false,
        };

        setMessages(prev => [...prev, assistantMessage]);

        // Stop thinking process
        setCurrentThinking(null);

        // Save assistant message to backend
        if (currentConversationId) {
          await addMessageToConversation(currentConversationId, 'assistant', assistantMessage.content);
        }
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      
      // For demonstration purposes, show thinking process even on error
      if (showThinkingProcess && currentThinking) {
        // Simulate a short thinking process for demo
        const thinkingEndTime = Date.now();
        const thinkingDuration = Math.max(2000, thinkingEndTime - thinkingStartTime); // Minimum 2 seconds for demo
        
        const demoMessage: Message = {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please make sure Ollama is running and try again.',
          timestamp: new Date().toISOString(),
          thinking: currentThinking.content + '\n\nEncountered connection error. Unable to process request.',
          thinkingDuration: thinkingDuration,
        };
        
        // Show the thinking process for a moment before the error message
        setTimeout(() => {
          setMessages(prev => [...prev, demoMessage]);
          setCurrentThinking(null);
          setIsLoading(false);
        }, 1500); // Wait 1.5 seconds to show the thinking animation
        
        return; // Don't set loading to false immediately
      }
      
      // Stop thinking process on error
      setCurrentThinking(null);
      
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please make sure Ollama is running and try again.',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
      setIsLoading(false);
    }
  };

  const toggleContextSources = (messageIndex: number) => {
    setShowContextSources(prev => ({
      ...prev,
      [messageIndex]: !prev[messageIndex]
    }));
  };

  const getSourceIcon = (type: string) => {
    switch (type) {
      case 'web_search':
        return <SearchIcon fontSize="small" />;
      case 'knowledge':
        return <StorageIcon fontSize="small" />;
      case 'conversation':
        return <ConversationIcon fontSize="small" />;
      default:
        return <StorageIcon fontSize="small" />;
    }
  };

  const getSourceLabel = (type: string) => {
    switch (type) {
      case 'web_search':
        return 'Web Search';
      case 'knowledge':
        return 'Knowledge Base';
      case 'conversation':
        return 'Previous Conversation';
      default:
        return 'Source';
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
                {/* Show thinking process for assistant messages */}
                {message.role === 'assistant' && showThinkingProcess && (
                  <ThinkingProcess
                    isThinking={currentThinking?.messageIndex === index}
                    thinkingContent={message.thinking || currentThinking?.content || ''}
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
                
                {/* Context Sources Display */}
                {message.role === 'assistant' && message.context_sources && message.context_sources.length > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      {message.rag_used && (
                        <Chip 
                          size="small" 
                          label="RAG Enhanced" 
                          color="primary" 
                          variant="outlined"
                        />
                      )}
                      {message.search_used && (
                        <Chip 
                          size="small" 
                          label="Web Search" 
                          color="secondary" 
                          variant="outlined"
                        />
                      )}
                      <Chip
                        size="small"
                        label={`${message.context_sources.length} source${message.context_sources.length !== 1 ? 's' : ''}`}
                        onClick={() => toggleContextSources(index)}
                        sx={{ cursor: 'pointer' }}
                      />
                    </Box>
                    
                    <Collapse in={showContextSources[index]}>
                      <List dense sx={{ bgcolor: 'rgba(255, 255, 255, 0.05)', borderRadius: 1, mt: 1 }}>
                        {message.context_sources.map((source, sourceIndex) => (
                          <ListItem key={sourceIndex} sx={{ py: 0.5 }}>
                            <ListItemIcon sx={{ minWidth: 30 }}>
                              {getSourceIcon(source.type)}
                            </ListItemIcon>
                            <ListItemText
                              primary={
                                source.url ? (
                                  <Link
                                    href={source.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    sx={{ 
                                      color: 'primary.light',
                                      textDecoration: 'none',
                                      '&:hover': { textDecoration: 'underline' },
                                      display: 'flex',
                                      alignItems: 'center',
                                      gap: 0.5
                                    }}
                                  >
                                    {source.title || getSourceLabel(source.type)}
                                    <OpenInNewIcon fontSize="small" />
                                  </Link>
                                ) : (
                                  source.title || getSourceLabel(source.type)
                                )
                              }
                              secondary={source.snippet}
                              primaryTypographyProps={{ 
                                fontSize: '0.875rem',
                                fontWeight: 500
                              }}
                              secondaryTypographyProps={{ 
                                fontSize: '0.75rem',
                                sx: { color: 'text.secondary' }
                              }}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Collapse>
                  </Box>
                )}
              </Paper>
            </Box>
          ))
        )}
        {/* Show thinking process for current message being processed */}
        {isLoading && currentThinking && (
          <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
            <Avatar sx={{ bgcolor: 'secondary.main', width: 32, height: 32 }}>
              <BotIcon />
            </Avatar>
            <Paper elevation={1} sx={{ p: 2, bgcolor: 'background.paper', flex: 1, maxWidth: '80%' }}>
              {showThinkingProcess && (
                <ThinkingProcess
                  isThinking={true}
                  thinkingContent={currentThinking.content}
                  showDropdown={false}
                />
              )}
              <CircularProgress size={20} />
            </Paper>
          </Box>
        )}
        {/* Fallback loading indicator when thinking is disabled */}
        {isLoading && !currentThinking && (
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