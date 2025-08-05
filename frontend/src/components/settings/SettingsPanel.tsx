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
      persistentMemory: false,
      ragEnabled: false,
      chromaDBUrl: 'http://localhost:8001',
      maxMemoryItems: 1000,
      
      // Web Search Settings
      webSearchEnabled: true, // Smart web search is always-on but activates when necessary
      searchEngine: 'duckduckgo',
      maxSearchResults: 5,
      
      // Search Engine Configurations
      searchEngines: {
        duckduckgo: {
          enabled: true,
          name: 'DuckDuckGo'
        },
        searxng: {
          enabled: false,
          name: 'SearXNG',
          instanceUrl: 'https://searx.be'
        },
        google: {
          enabled: false,
          name: 'Google Custom Search',
          apiKey: '',
          cx: ''
        },
        bing: {
          enabled: false,
          name: 'Bing Search',
          apiKey: ''
        }
      },
      
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

  const handleSave = async () => {
    try {
      // Save settings to localStorage
      localStorage.setItem('evolveui-settings', JSON.stringify(settings));
      
      // Send search engine configuration to backend
      if (settings.searchEngines) {
        const searchConfig = {
          default_engine: settings.searchEngine,
          engines: {
            duckduckgo: {
              enabled: settings.searchEngines.duckduckgo.enabled
            },
            searxng: {
              enabled: settings.searchEngines.searxng.enabled,
              instance_url: settings.searchEngines.searxng.instanceUrl
            },
            google: {
              enabled: settings.searchEngines.google.enabled,
              api_key: settings.searchEngines.google.apiKey,
              cx: settings.searchEngines.google.cx
            },
            bing: {
              enabled: settings.searchEngines.bing.enabled,
              api_key: settings.searchEngines.bing.apiKey
            }
          }
        };
        
        try {
          const response = await fetch('http://localhost:8000/api/search/config', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(searchConfig)
          });
          
          if (!response.ok) {
            console.warn('Failed to update search configuration on backend');
          }
        } catch (error) {
          console.warn('Failed to connect to backend for search configuration:', error);
        }
      }
      
      console.log('Settings saved successfully:', settings);
      onClose();
    } catch (error) {
      console.error('Error saving settings:', error);
    }
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
                
                <TextField
                  label="ChromaDB URL"
                  value={settings.chromaDBUrl}
                  onChange={(e) => handleSettingChange('chromaDBUrl', e.target.value)}
                  fullWidth
                  size="small"
                  disabled={!settings.ragEnabled}
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
                
                <TextField
                  label="Default Search Engine"
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
                  <option value="searxng">SearXNG</option>
                  <option value="google">Google Custom Search</option>
                  <option value="bing">Bing Search</option>
                </TextField>
                
                <TextField
                  label="Max Search Results"
                  type="number"
                  value={settings.maxSearchResults}
                  onChange={(e) => handleSettingChange('maxSearchResults', parseInt(e.target.value))}
                  fullWidth
                  size="small"
                  disabled={!settings.webSearchEnabled}
                />

                <Typography variant="h6" sx={{ mt: 2 }}>
                  Search Engine Configuration
                </Typography>

                {/* DuckDuckGo Configuration */}
                <Box sx={{ border: '1px solid rgba(255, 255, 255, 0.12)', borderRadius: 1, p: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    DuckDuckGo
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Free search engine, no API key required
                  </Typography>
                  <FormControlLabel
                    control={
                      <Switch 
                        checked={settings.searchEngines.duckduckgo.enabled}
                        onChange={(e) => handleSettingChange('searchEngines', {
                          ...settings.searchEngines,
                          duckduckgo: { ...settings.searchEngines.duckduckgo, enabled: e.target.checked }
                        })}
                      />
                    }
                    label="Enable DuckDuckGo"
                  />
                </Box>

                {/* SearXNG Configuration */}
                <Box sx={{ border: '1px solid rgba(255, 255, 255, 0.12)', borderRadius: 1, p: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    SearXNG
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Self-hosted search engine aggregator, no API key required
                  </Typography>
                  <FormControlLabel
                    control={
                      <Switch 
                        checked={settings.searchEngines.searxng.enabled}
                        onChange={(e) => handleSettingChange('searchEngines', {
                          ...settings.searchEngines,
                          searxng: { ...settings.searchEngines.searxng, enabled: e.target.checked }
                        })}
                      />
                    }
                    label="Enable SearXNG"
                  />
                  <TextField
                    label="SearXNG Instance URL"
                    value={settings.searchEngines.searxng.instanceUrl}
                    onChange={(e) => handleSettingChange('searchEngines', {
                      ...settings.searchEngines,
                      searxng: { ...settings.searchEngines.searxng, instanceUrl: e.target.value }
                    })}
                    fullWidth
                    size="small"
                    disabled={!settings.searchEngines.searxng.enabled}
                    placeholder="https://searx.be"
                    sx={{ mt: 1 }}
                  />
                </Box>

                {/* Google Configuration */}
                <Box sx={{ border: '1px solid rgba(255, 255, 255, 0.12)', borderRadius: 1, p: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Google Custom Search
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Requires Google Cloud API key and Custom Search Engine ID
                  </Typography>
                  <FormControlLabel
                    control={
                      <Switch 
                        checked={settings.searchEngines.google.enabled}
                        onChange={(e) => handleSettingChange('searchEngines', {
                          ...settings.searchEngines,
                          google: { ...settings.searchEngines.google, enabled: e.target.checked }
                        })}
                      />
                    }
                    label="Enable Google Search"
                  />
                  <TextField
                    label="Google API Key"
                    value={settings.searchEngines.google.apiKey}
                    onChange={(e) => handleSettingChange('searchEngines', {
                      ...settings.searchEngines,
                      google: { ...settings.searchEngines.google, apiKey: e.target.value }
                    })}
                    fullWidth
                    size="small"
                    disabled={!settings.searchEngines.google.enabled}
                    type="password"
                    sx={{ mt: 1 }}
                  />
                  <TextField
                    label="Custom Search Engine ID (CX)"
                    value={settings.searchEngines.google.cx}
                    onChange={(e) => handleSettingChange('searchEngines', {
                      ...settings.searchEngines,
                      google: { ...settings.searchEngines.google, cx: e.target.value }
                    })}
                    fullWidth
                    size="small"
                    disabled={!settings.searchEngines.google.enabled}
                    sx={{ mt: 1 }}
                  />
                </Box>

                {/* Bing Configuration */}
                <Box sx={{ border: '1px solid rgba(255, 255, 255, 0.12)', borderRadius: 1, p: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Bing Search
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Requires Microsoft Azure Cognitive Services API key
                  </Typography>
                  <FormControlLabel
                    control={
                      <Switch 
                        checked={settings.searchEngines.bing.enabled}
                        onChange={(e) => handleSettingChange('searchEngines', {
                          ...settings.searchEngines,
                          bing: { ...settings.searchEngines.bing, enabled: e.target.checked }
                        })}
                      />
                    }
                    label="Enable Bing Search"
                  />
                  <TextField
                    label="Bing API Key"
                    value={settings.searchEngines.bing.apiKey}
                    onChange={(e) => handleSettingChange('searchEngines', {
                      ...settings.searchEngines,
                      bing: { ...settings.searchEngines.bing, apiKey: e.target.value }
                    })}
                    fullWidth
                    size="small"
                    disabled={!settings.searchEngines.bing.enabled}
                    type="password"
                    sx={{ mt: 1 }}
                  />
                </Box>
              </Box>
            </TabPanel>

            {/* Evolver Settings */}
            <TabPanel value={tabValue} index={3}>
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
            <TabPanel value={tabValue} index={4}>
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