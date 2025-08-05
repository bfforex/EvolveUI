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
import { FileUploadDialog } from './components/chat/FileUploadDialog';
import { CodeExecutionDialog } from './components/chat/CodeExecutionDialog';
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
  const [isCodeExecutionOpen, setIsCodeExecutionOpen] = useState(false);
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
      persistentMemory: true,
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
          onOpenFileUpload={() => setIsFileUploadOpen(true)}
          onOpenCodeExecution={() => setIsCodeExecutionOpen(true)}
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
            settings={settings}
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

        {/* File Upload Dialog */}
        <FileUploadDialog
          open={isFileUploadOpen}
          onClose={() => setIsFileUploadOpen(false)}
          onUploadComplete={(results) => {
            console.log('Files uploaded:', results);
            // Optionally show notification or refresh knowledge base
          }}
        />

        {/* Code Execution Dialog */}
        <CodeExecutionDialog
          open={isCodeExecutionOpen}
          onClose={() => setIsCodeExecutionOpen(false)}
        />
      </Box>
    </ThemeProvider>
  );
}

export default App;
