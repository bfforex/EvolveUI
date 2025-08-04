import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import { ConversationPanel } from './components/conversations/ConversationPanel';
import { ChatPanel } from './components/chat/ChatPanel';
import { WorkpadPanel } from './components/workpad/WorkpadPanel';
import { TopBar } from './components/layout/TopBar';
import { SettingsPanel } from './components/settings/SettingsPanel';
import { KnowledgePanel } from './components/settings/KnowledgePanel';
import { FileUploadPanel } from './components/files/FileUploadPanel';
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
      default: '#0D1117', // GitHub-style dark background
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
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isKnowledgeOpen, setIsKnowledgeOpen] = useState(false);
  const [isFileUploadOpen, setIsFileUploadOpen] = useState(false);
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null);
  
  // Load settings from localStorage
  const [settings, setSettings] = useState(() => {
    const saved = localStorage.getItem('evolveui-settings');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (error) {
        console.error('Failed to parse saved settings:', error);
      }
    }
    return {
      showThinkingProcess: false,
      webSearchEnabled: true,
      evolverEnabled: false,
      ragEnabled: true,
      fileProcessingEnabled: true,
      codeExecutionEnabled: true,
      persistentMemory: true,
      contextLimit: 3,
      autoAddConversations: true,
      autoWebSearch: true,
      autoAddFilesToKnowledge: true,
    };
  });

  // Listen for settings changes
  React.useEffect(() => {
    const handleStorageChange = () => {
      const saved = localStorage.getItem('evolveui-settings');
      if (saved) {
        try {
          setSettings(JSON.parse(saved));
        } catch (error) {
          console.error('Failed to parse saved settings:', error);
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

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
          onOpenSettings={() => setIsSettingsOpen(true)}
          onOpenKnowledge={() => setIsKnowledgeOpen(true)}
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
            showThinkingProcess={settings.showThinkingProcess}
            webSearchEnabled={settings.webSearchEnabled}
            evolverEnabled={settings.evolverEnabled}
            ragEnabled={settings.ragEnabled}
            contextLimit={settings.contextLimit}
            onOpenFileUpload={() => setIsFileUploadOpen(true)}
          />
          
          {/* Right Panel - Workpad */}
          {isWorkpadOpen && (
            <WorkpadPanel onClose={() => setIsWorkpadOpen(false)} />
          )}
        </Box>

        {/* Settings Panel */}
        <SettingsPanel 
          open={isSettingsOpen}
          onClose={() => setIsSettingsOpen(false)}
        />

        {/* Knowledge Panel */}
        <KnowledgePanel 
          open={isKnowledgeOpen}
          onClose={() => setIsKnowledgeOpen(false)}
        />

        {/* File Upload Panel */}
        <FileUploadPanel 
          open={isFileUploadOpen}
          onClose={() => setIsFileUploadOpen(false)}
          onFileProcessed={(result) => {
            console.log('File processed:', result);
            // Optionally trigger refresh of knowledge base or other actions
          }}
        />
      </Box>
    </ThemeProvider>
  );
}

export default App;
