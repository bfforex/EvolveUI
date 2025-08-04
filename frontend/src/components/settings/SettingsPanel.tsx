import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Switch,
  FormControlLabel,
  TextField,
  Tabs,
  Tab,
  Paper,
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Memory as MemoryIcon,
  Search as SearchIcon,
  Palette as PaletteIcon,
  Code as CodeIcon,
  Psychology as PsychologyIcon,
  Upload as UploadIcon,
  PlayArrow as ExecuteIcon,
} from '@mui/icons-material';

interface SettingsPanelProps {
  open: boolean;
  onClose: () => void;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`settings-tabpanel-${index}`}
      aria-labelledby={`settings-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

export const SettingsPanel: React.FC<SettingsPanelProps> = ({ open, onClose }) => {
  const [tabValue, setTabValue] = useState(0);
  
  // Load settings from localStorage
  const loadSettings = () => {
    const saved = localStorage.getItem('evolveui-settings');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (error) {
        console.error('Failed to parse saved settings:', error);
      }
    }
    return {
      // UI Settings
      darkMode: true,
      compactMode: false,
      showTimestamps: true,
      showThinkingProcess: false,
      
      // Memory/RAG Settings
      persistentMemory: true,
      ragEnabled: true,
      chromaDBUrl: 'http://localhost:8001',
      maxMemoryItems: 1000,
      contextLimit: 3,
      autoAddConversations: true,
      
      // Web Search Settings
      webSearchEnabled: true, // Smart web search is always-on but activates when necessary
      searchEngine: 'duckduckgo',
      maxSearchResults: 5,
      autoWebSearch: true,
      
      // File Processing Settings
      fileProcessingEnabled: true,
      autoAddFilesToKnowledge: true,
      supportedFileTypes: ['.txt', '.md', '.pdf', '.docx', '.py', '.js', '.json', '.csv'],
      maxFileSize: 10, // MB
      
      // Code Execution Settings
      codeExecutionEnabled: true,
      allowedLanguages: ['python', 'javascript'],
      executionTimeout: 30, // seconds
      safeMode: true,
      
      // Evolver Settings
      evolverEnabled: false,
      learningEnabled: false,
      scheduledSearchEnabled: false,
      
      // Model Settings
      defaultModel: 'llama3.2',
      maxTokens: 2048,
      temperature: 0.7,
      streamResponses: true,
    };
  };
  
  const [settings, setSettings] = useState(loadSettings());

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleSettingChange = (setting: string, value: any) => {
    setSettings((prev: any) => ({ ...prev, [setting]: value }));
  };

  const handleSave = () => {
    // Save settings to localStorage
    localStorage.setItem('evolveui-settings', JSON.stringify(settings));
    console.log('Saving settings:', settings);
    onClose();
  };

  const handleReset = () => {
    // TODO: Reset to default settings
    console.log('Resetting settings to defaults');
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="md" 
      fullWidth
      PaperProps={{
        sx: {
          bgcolor: 'background.paper',
          minHeight: '70vh',
        }
      }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <SettingsIcon />
          Settings
        </Box>
      </DialogTitle>
      
      <DialogContent sx={{ p: 0 }}>
        <Box sx={{ display: 'flex', height: '500px' }}>
          {/* Settings Navigation */}
          <Paper 
            elevation={0}
            sx={{ 
              width: 200, 
              borderRight: '1px solid rgba(255, 255, 255, 0.12)',
              bgcolor: 'background.default'
            }}
          >
            <Tabs
              orientation="vertical"
              value={tabValue}
              onChange={handleTabChange}
              sx={{ 
                borderRight: 1, 
                borderColor: 'divider',
                '& .MuiTab-root': {
                  alignItems: 'flex-start',
                  textAlign: 'left',
                  minHeight: 60,
                }
              }}
            >
              <Tab 
                icon={<PaletteIcon />} 
                label="Appearance" 
                iconPosition="start"
                sx={{ justifyContent: 'flex-start' }}
              />
              <Tab 
                icon={<MemoryIcon />} 
                label="Memory & RAG" 
                iconPosition="start"
                sx={{ justifyContent: 'flex-start' }}
              />
              <Tab 
                icon={<SearchIcon />} 
                label="Web Search" 
                iconPosition="start"
                sx={{ justifyContent: 'flex-start' }}
              />
              <Tab 
                icon={<UploadIcon />} 
                label="File Processing" 
                iconPosition="start"
                sx={{ justifyContent: 'flex-start' }}
              />
              <Tab 
                icon={<ExecuteIcon />} 
                label="Code Execution" 
                iconPosition="start"
                sx={{ justifyContent: 'flex-start' }}
              />
              <Tab 
                icon={<PsychologyIcon />} 
                label="Evolver" 
                iconPosition="start"
                sx={{ justifyContent: 'flex-start' }}
              />
              <Tab 
                icon={<CodeIcon />} 
                label="Models" 
                iconPosition="start"
                sx={{ justifyContent: 'flex-start' }}
              />
            </Tabs>
          </Paper>

          {/* Settings Content */}
          <Box sx={{ flex: 1, overflow: 'auto' }}>
            {/* Appearance Settings */}
            <TabPanel value={tabValue} index={0}>
              <Typography variant="h6" gutterBottom>
                Appearance Settings
              </Typography>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <FormControlLabel
                  control={
                    <Switch 
                      checked={settings.darkMode}
                      onChange={(e) => handleSettingChange('darkMode', e.target.checked)}
                    />
                  }
                  label="Dark Mode"
                />
                
                <FormControlLabel
                  control={
                    <Switch 
                      checked={settings.compactMode}
                      onChange={(e) => handleSettingChange('compactMode', e.target.checked)}
                    />
                  }
                  label="Compact Mode"
                />
                
                <FormControlLabel
                  control={
                    <Switch 
                      checked={settings.showTimestamps}
                      onChange={(e) => handleSettingChange('showTimestamps', e.target.checked)}
                    />
                  }
                  label="Show Message Timestamps"
                />
                
                <FormControlLabel
                  control={
                    <Switch 
                      checked={settings.showThinkingProcess}
                      onChange={(e) => handleSettingChange('showThinkingProcess', e.target.checked)}
                    />
                  }
                  label="Show AI Thinking Process"
                />
                <Typography variant="caption" color="text.secondary" sx={{ ml: 4, mt: -1 }}>
                  Display AI thought processes in gray text similar to Microsoft Copilot
                </Typography>
              </Box>
            </TabPanel>

            {/* Memory & RAG Settings */}
            <TabPanel value={tabValue} index={1}>
              <Typography variant="h6" gutterBottom>
                Memory & RAG Settings
              </Typography>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <FormControlLabel
                  control={
                    <Switch 
                      checked={settings.persistentMemory}
                      onChange={(e) => handleSettingChange('persistentMemory', e.target.checked)}
                    />
                  }
                  label="Enable Persistent Memory"
                />
                
                <FormControlLabel
                  control={
                    <Switch 
                      checked={settings.ragEnabled}
                      onChange={(e) => handleSettingChange('ragEnabled', e.target.checked)}
                    />
                  }
                  label="Enable RAG (Retrieval Augmented Generation)"
                />
                
                <FormControlLabel
                  control={
                    <Switch 
                      checked={settings.autoAddConversations}
                      onChange={(e) => handleSettingChange('autoAddConversations', e.target.checked)}
                      disabled={!settings.ragEnabled}
                    />
                  }
                  label="Auto-add conversations to knowledge base"
                />
                
                <TextField
                  label="ChromaDB URL"
                  value={settings.chromaDBUrl}
                  onChange={(e) => handleSettingChange('chromaDBUrl', e.target.value)}
                  fullWidth
                  size="small"
                  disabled={!settings.ragEnabled}
                />
                
                <TextField
                  label="Context Limit (documents per query)"
                  type="number"
                  value={settings.contextLimit}
                  onChange={(e) => handleSettingChange('contextLimit', parseInt(e.target.value))}
                  fullWidth
                  size="small"
                  disabled={!settings.ragEnabled}
                  inputProps={{ min: 1, max: 10 }}
                />
                
                <TextField
                  label="Max Memory Items"
                  type="number"
                  value={settings.maxMemoryItems}
                  onChange={(e) => handleSettingChange('maxMemoryItems', parseInt(e.target.value))}
                  fullWidth
                  size="small"
                  disabled={!settings.persistentMemory}
                />
              </Box>
            </TabPanel>

            {/* Web Search Settings */}
            <TabPanel value={tabValue} index={2}>
              <Typography variant="h6" gutterBottom>
                Smart Web Search
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom sx={{ mb: 2 }}>
                Smart Web Search is always-on but activates only when necessary to provide up-to-date information.
              </Typography>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <FormControlLabel
                  control={
                    <Switch 
                      checked={settings.webSearchEnabled}
                      onChange={(e) => handleSettingChange('webSearchEnabled', e.target.checked)}
                    />
                  }
                  label="Enable Smart Web Search"
                />
                
                <FormControlLabel
                  control={
                    <Switch 
                      checked={settings.autoWebSearch}
                      onChange={(e) => handleSettingChange('autoWebSearch', e.target.checked)}
                      disabled={!settings.webSearchEnabled}
                    />
                  }
                  label="Auto-trigger web search when needed"
                />
                
                <TextField
                  label="Search Engine"
                  select
                  value={settings.searchEngine}
                  onChange={(e) => handleSettingChange('searchEngine', e.target.value)}
                  fullWidth
                  size="small"
                  disabled={!settings.webSearchEnabled}
                  SelectProps={{
                    native: true,
                  }}
                >
                  <option value="duckduckgo">DuckDuckGo</option>
                  <option value="bing">Bing</option>
                  <option value="google">Google (API Key Required)</option>
                </TextField>
                
                <TextField
                  label="Max Search Results"
                  type="number"
                  value={settings.maxSearchResults}
                  onChange={(e) => handleSettingChange('maxSearchResults', parseInt(e.target.value))}
                  fullWidth
                  size="small"
                  disabled={!settings.webSearchEnabled}
                  inputProps={{ min: 1, max: 10 }}
                />
              </Box>
            </TabPanel>

            {/* File Processing Settings */}
            <TabPanel value={tabValue} index={3}>
              <Typography variant="h6" gutterBottom>
                File Processing
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom sx={{ mb: 2 }}>
                Configure file upload and processing capabilities including PDF, DOCX, and text files.
              </Typography>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <FormControlLabel
                  control={
                    <Switch 
                      checked={settings.fileProcessingEnabled}
                      onChange={(e) => handleSettingChange('fileProcessingEnabled', e.target.checked)}
                    />
                  }
                  label="Enable File Processing"
                />
                
                <FormControlLabel
                  control={
                    <Switch 
                      checked={settings.autoAddFilesToKnowledge}
                      onChange={(e) => handleSettingChange('autoAddFilesToKnowledge', e.target.checked)}
                      disabled={!settings.fileProcessingEnabled || !settings.ragEnabled}
                    />
                  }
                  label="Auto-add uploaded files to knowledge base"
                />
                
                <TextField
                  label="Max File Size (MB)"
                  type="number"
                  value={settings.maxFileSize}
                  onChange={(e) => handleSettingChange('maxFileSize', parseInt(e.target.value))}
                  fullWidth
                  size="small"
                  disabled={!settings.fileProcessingEnabled}
                  inputProps={{ min: 1, max: 100 }}
                />
                
                <Typography variant="body2" color="text.secondary">
                  Supported file types: PDF, DOCX, TXT, MD, PY, JS, JSON, CSV
                </Typography>
              </Box>
            </TabPanel>

            {/* Code Execution Settings */}
            <TabPanel value={tabValue} index={4}>
              <Typography variant="h6" gutterBottom>
                Code Execution
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom sx={{ mb: 2 }}>
                Enable safe code execution environment for Python, JavaScript, and other languages.
              </Typography>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <FormControlLabel
                  control={
                    <Switch 
                      checked={settings.codeExecutionEnabled}
                      onChange={(e) => handleSettingChange('codeExecutionEnabled', e.target.checked)}
                    />
                  }
                  label="Enable Code Execution"
                />
                
                <FormControlLabel
                  control={
                    <Switch 
                      checked={settings.safeMode}
                      onChange={(e) => handleSettingChange('safeMode', e.target.checked)}
                      disabled={!settings.codeExecutionEnabled}
                    />
                  }
                  label="Safe Mode (blocks dangerous operations)"
                />
                
                <TextField
                  label="Execution Timeout (seconds)"
                  type="number"
                  value={settings.executionTimeout}
                  onChange={(e) => handleSettingChange('executionTimeout', parseInt(e.target.value))}
                  fullWidth
                  size="small"
                  disabled={!settings.codeExecutionEnabled}
                  inputProps={{ min: 5, max: 120 }}
                />
                
                <Typography variant="body2" color="text.secondary">
                  Supported languages: Python, JavaScript, Bash (limited)
                </Typography>
                
                <Typography variant="caption" color="warning.main">
                  ⚠️ Code execution runs in a sandboxed environment but use caution with untrusted code.
                </Typography>
              </Box>
            </TabPanel>

            {/* Evolver Settings */}
            <TabPanel value={tabValue} index={5}>
              <Typography variant="h6" gutterBottom>
                Evolver System
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom sx={{ mb: 2 }}>
                Enable model learning through user interactions and proactive knowledge growth.
              </Typography>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <FormControlLabel
                  control={
                    <Switch 
                      checked={settings.evolverEnabled}
                      onChange={(e) => handleSettingChange('evolverEnabled', e.target.checked)}
                    />
                  }
                  label="Enable Evolver System"
                />
                
                <FormControlLabel
                  control={
                    <Switch 
                      checked={settings.learningEnabled}
                      onChange={(e) => handleSettingChange('learningEnabled', e.target.checked)}
                      disabled={!settings.evolverEnabled}
                    />
                  }
                  label="Enable Learning from Interactions"
                />
                
                <FormControlLabel
                  control={
                    <Switch 
                      checked={settings.scheduledSearchEnabled}
                      onChange={(e) => handleSettingChange('scheduledSearchEnabled', e.target.checked)}
                      disabled={!settings.evolverEnabled}
                    />
                  }
                  label="Enable Scheduled Knowledge Searches"
                />
                
                <Typography variant="caption" color="text.secondary">
                  Advanced features coming soon: Deep Research capability and Agenic Workflow for task automation.
                </Typography>
              </Box>
            </TabPanel>

            {/* Model Settings */}
            <TabPanel value={tabValue} index={6}>
              <Typography variant="h6" gutterBottom>
                Model Settings
              </Typography>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <TextField
                  label="Default Model"
                  value={settings.defaultModel}
                  onChange={(e) => handleSettingChange('defaultModel', e.target.value)}
                  fullWidth
                  size="small"
                />
                
                <TextField
                  label="Max Tokens"
                  type="number"
                  value={settings.maxTokens}
                  onChange={(e) => handleSettingChange('maxTokens', parseInt(e.target.value))}
                  fullWidth
                  size="small"
                />
                
                <TextField
                  label="Temperature"
                  type="number"
                  value={settings.temperature}
                  onChange={(e) => handleSettingChange('temperature', parseFloat(e.target.value))}
                  fullWidth
                  size="small"
                  inputProps={{ min: 0, max: 2, step: 0.1 }}
                />
                
                <FormControlLabel
                  control={
                    <Switch 
                      checked={settings.streamResponses}
                      onChange={(e) => handleSettingChange('streamResponses', e.target.checked)}
                    />
                  }
                  label="Stream Responses"
                />
              </Box>
            </TabPanel>
          </Box>
        </Box>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={handleReset} color="secondary">
          Reset to Defaults
        </Button>
        <Button onClick={onClose}>
          Cancel
        </Button>
        <Button onClick={handleSave} variant="contained">
          Save Settings
        </Button>
      </DialogActions>
    </Dialog>
  );
};