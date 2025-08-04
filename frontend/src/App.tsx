import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import { ConversationPanel } from './components/conversations/ConversationPanel';
import { ChatPanel } from './components/chat/ChatPanel';
import { WorkpadPanel } from './components/workpad/WorkpadPanel';
import { TopBar } from './components/layout/TopBar';
import './App.css';

// Create dark theme matching the color scheme requirements
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#1976d2', // Deep blue
    },
    secondary: {
      main: '#ffd700', // Gold accent
    },
    background: {
      default: '#0a1929', // Deep dark blue
      paper: '#1a2332', // Dark blue
    },
    text: {
      primary: '#ffffff',
      secondary: '#b0bec5', // Grayish blue
    },
  },
});

function App() {
  const [isConversationPanelOpen, setIsConversationPanelOpen] = useState(true);
  const [isWorkpadOpen, setIsWorkpadOpen] = useState(false);
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null);

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column', 
        height: '100vh',
        bgcolor: 'background.default'
      }}>
        {/* Top Bar */}
        <TopBar 
          onToggleConversations={() => setIsConversationPanelOpen(!isConversationPanelOpen)}
          onToggleWorkpad={() => setIsWorkpadOpen(!isWorkpadOpen)}
          isWorkpadOpen={isWorkpadOpen}
        />
        
        {/* Main Content Area */}
        <Box sx={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
          {/* Left Panel - Conversations */}
          <ConversationPanel 
            isOpen={isConversationPanelOpen}
            selectedConversationId={selectedConversationId}
            onSelectConversation={setSelectedConversationId}
          />
          
          {/* Center Panel - Chat */}
          <ChatPanel 
            conversationId={selectedConversationId}
            onNewConversation={(id) => setSelectedConversationId(id)}
          />
          
          {/* Right Panel - Workpad */}
          {isWorkpadOpen && (
            <WorkpadPanel onClose={() => setIsWorkpadOpen(false)} />
          )}
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;
