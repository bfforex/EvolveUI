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
import { ThinkingDemo } from './components/chat/ThinkingDemo';
import './App.css';

// Create minimalist all-black theme
const minimalistBlackTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#ffffff', // White for primary elements on black
      contrastText: '#000000',
    },
    secondary: {
      main: '#888888', // Subtle gray accent
      contrastText: '#ffffff',
    },
    background: {
      default: '#000000', // Pure black background
      paper: '#111111', // Very dark gray for cards/panels
    },
    text: {
      primary: '#ffffff', // White text
      secondary: '#cccccc', // Light gray for secondary text
    },
    divider: '#333333', // Dark gray for dividers
    action: {
      hover: '#222222', // Subtle hover effect
      selected: '#333333', // Selection background
    },
  },
  components: {
    // Override component styles for all-black theme
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundColor: '#111111',
          borderColor: '#333333',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#000000',
          borderBottom: '1px solid #333333',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderColor: '#333333',
          '&:hover': {
            backgroundColor: '#222222',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            '& fieldset': {
              borderColor: '#333333',
            },
            '&:hover fieldset': {
              borderColor: '#555555',
            },
            '&.Mui-focused fieldset': {
              borderColor: '#ffffff',
            },
          },
        },
      },
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
  const [showDemo, setShowDemo] = useState(false);
  
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
    <ThemeProvider theme={minimalistBlackTheme}>
      <CssBaseline />
      
      {/* Show demo if requested */}
      {showDemo ? (
        <Box sx={{ position: 'relative' }}>
          <Box sx={{ position: 'absolute', top: 16, right: 16, zIndex: 1000 }}>
            <button 
              onClick={() => setShowDemo(false)}
              style={{
                background: '#ffffff',
                color: '#000000',
                border: '1px solid #333333',
                padding: '8px 16px',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Back to Main App
            </button>
          </Box>
          <ThinkingDemo />
        </Box>
      ) : (
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
          
          {/* Demo button */}
          <Box sx={{ position: 'absolute', top: 80, right: 16, zIndex: 1000 }}>
            <button 
              onClick={() => setShowDemo(true)}
              style={{
                background: '#888888',
                color: '#ffffff',
                border: '1px solid #333333',
                padding: '8px 16px',
                borderRadius: '4px',
                cursor: 'pointer',
                fontWeight: 'bold'
              }}
            >
              Show Thinking Process Demo
            </button>
          </Box>
          
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
      )}
    </ThemeProvider>
  );
}

export default App;
