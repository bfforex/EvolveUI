import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Tabs,
  Tab,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import {
  Close as CloseIcon,
  Code as CodeIcon,
  Description as DocumentIcon,
  Download as DownloadIcon,
  Upload as UploadIcon,
  PlayArrow as RunIcon,
} from '@mui/icons-material';
import axios from 'axios';

interface WorkpadPanelProps {
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
      id={`workpad-tabpanel-${index}`}
      aria-labelledby={`workpad-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 2, height: '100%' }}>
          {children}
        </Box>
      )}
    </div>
  );
}

export const WorkpadPanel: React.FC<WorkpadPanelProps> = ({ onClose }) => {
  const [tabValue, setTabValue] = useState(0);
  const [codeContent, setCodeContent] = useState('// Your code here\nconsole.log("Hello, EvolveUI!");');
  const [documentContent, setDocumentContent] = useState('# Document Title\n\nYour document content here...');
  const [selectedLanguage, setSelectedLanguage] = useState('python');
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const executeCode = async () => {
    if (!codeContent.trim()) {
      setError('No code to execute');
      return;
    }

    setIsExecuting(true);
    setError(null);
    setExecutionResult(null);

    try {
      const response = await axios.post('http://localhost:8000/api/code/execute', {
        code: codeContent,
        language: selectedLanguage,
      });

      setExecutionResult(response.data.execution_result);
    } catch (error: any) {
      console.error('Code execution error:', error);
      setError(error.response?.data?.detail || error.message);
    } finally {
      setIsExecuting(false);
    }
  };

  const validateCode = async () => {
    if (!codeContent.trim()) return;

    try {
      const response = await axios.post('http://localhost:8000/api/code/validate', {
        code: codeContent,
        language: selectedLanguage,
      });

      if (!response.data.validation.valid) {
        setError(`Validation errors: ${response.data.validation.errors.join(', ')}`);
      } else {
        setError(null);
      }
    } catch (error: any) {
      console.error('Code validation error:', error);
    }
  };

  React.useEffect(() => {
    if (tabValue === 0 && codeContent.trim()) {
      // Debounce validation
      const timeoutId = setTimeout(validateCode, 1000);
      return () => clearTimeout(timeoutId);
    }
  }, [codeContent, selectedLanguage]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
    setExecutionResult(null);
    setError(null);
  };

  const downloadContent = () => {
    const content = tabValue === 0 ? codeContent : documentContent;
    const filename = tabValue === 0 ? 'code.js' : 'document.md';
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        if (tabValue === 0) {
          setCodeContent(content);
        } else {
          setDocumentContent(content);
        }
      };
      reader.readAsText(file);
    }
  };

  return (
    <Paper
      elevation={2}
      sx={{
        width: 400,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: 'background.paper',
        borderLeft: '1px solid rgba(255, 255, 255, 0.12)',
      }}
    >
      {/* Header */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          p: 2,
          borderBottom: '1px solid rgba(255, 255, 255, 0.12)',
        }}
      >
        <Typography variant="h6" sx={{ fontWeight: 600 }}>
          Workpad
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <input
            accept="*"
            style={{ display: 'none' }}
            id="upload-file"
            type="file"
            onChange={handleFileUpload}
          />
          <label htmlFor="upload-file">
            <IconButton size="small" component="span">
              <UploadIcon />
            </IconButton>
          </label>
          <IconButton size="small" onClick={downloadContent}>
            <DownloadIcon />
          </IconButton>
          <IconButton size="small" onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Box>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          variant="fullWidth"
        >
          <Tab
            icon={<CodeIcon />}
            label="Code"
            id="workpad-tab-0"
            aria-controls="workpad-tabpanel-0"
          />
          <Tab
            icon={<DocumentIcon />}
            label="Docs"
            id="workpad-tab-1"
            aria-controls="workpad-tabpanel-1"
          />
        </Tabs>
      </Box>

      {/* Content */}
      <Box sx={{ flex: 1, overflow: 'hidden' }}>
        <TabPanel value={tabValue} index={0}>
          <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Code Editor
              </Typography>
              <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel>Language</InputLabel>
                <Select
                  value={selectedLanguage}
                  onChange={(e) => setSelectedLanguage(e.target.value)}
                  label="Language"
                >
                  <MenuItem value="python">Python</MenuItem>
                  <MenuItem value="javascript">JavaScript</MenuItem>
                  <MenuItem value="bash">Bash</MenuItem>
                </Select>
              </FormControl>
            </Box>
            
            {error && (
              <Alert severity="error" sx={{ mb: 1 }}>
                {error}
              </Alert>
            )}
            
            <TextField
              fullWidth
              multiline
              value={codeContent}
              onChange={(e) => setCodeContent(e.target.value)}
              variant="outlined"
              sx={{
                flex: 1,
                '& .MuiInputBase-root': {
                  height: '100%',
                  alignItems: 'flex-start',
                },
                '& .MuiInputBase-input': {
                  fontFamily: 'Monaco, Consolas, "Courier New", monospace',
                  fontSize: '0.875rem',
                  height: '100% !important',
                  overflow: 'auto !important',
                },
              }}
              placeholder="Write your code here..."
            />
            
            <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
              <Button
                variant="contained"
                size="small"
                onClick={executeCode}
                disabled={isExecuting || !codeContent.trim()}
                startIcon={isExecuting ? <CircularProgress size={16} /> : <RunIcon />}
              >
                {isExecuting ? 'Running...' : 'Run Code'}
              </Button>
              <Button
                variant="outlined"
                size="small"
                onClick={() => {
                  setCodeContent('');
                  setExecutionResult(null);
                  setError(null);
                }}
              >
                Clear
              </Button>
            </Box>
            
            {/* Execution Results */}
            {executionResult && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" sx={{ mb: 1 }}>
                  Execution Result
                </Typography>
                <Paper 
                  variant="outlined" 
                  sx={{ 
                    p: 2, 
                    bgcolor: executionResult.success ? 'rgba(76, 175, 80, 0.1)' : 'rgba(244, 67, 54, 0.1)',
                    maxHeight: 200,
                    overflow: 'auto'
                  }}
                >
                  {executionResult.output && (
                    <Box sx={{ mb: 1 }}>
                      <Typography variant="caption" color="text.secondary">Output:</Typography>
                      <Typography 
                        variant="body2" 
                        component="pre" 
                        sx={{ 
                          fontFamily: 'Monaco, Consolas, "Courier New", monospace',
                          fontSize: '0.75rem',
                          whiteSpace: 'pre-wrap',
                          wordWrap: 'break-word'
                        }}
                      >
                        {executionResult.output}
                      </Typography>
                    </Box>
                  )}
                  
                  {executionResult.stderr && (
                    <Box sx={{ mb: 1 }}>
                      <Typography variant="caption" color="error">Errors:</Typography>
                      <Typography 
                        variant="body2" 
                        component="pre" 
                        color="error"
                        sx={{ 
                          fontFamily: 'Monaco, Consolas, "Courier New", monospace',
                          fontSize: '0.75rem',
                          whiteSpace: 'pre-wrap',
                          wordWrap: 'break-word'
                        }}
                      >
                        {executionResult.stderr}
                      </Typography>
                    </Box>
                  )}
                  
                  <Typography variant="caption" color="text.secondary">
                    Execution time: {executionResult.execution_time}s | 
                    Return code: {executionResult.return_code} |
                    Status: {executionResult.success ? 'Success' : 'Failed'}
                  </Typography>
                </Paper>
              </Box>
            )}
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Typography variant="subtitle2" sx={{ mb: 1, color: 'text.secondary' }}>
              Document Editor
            </Typography>
            <TextField
              fullWidth
              multiline
              value={documentContent}
              onChange={(e) => setDocumentContent(e.target.value)}
              variant="outlined"
              sx={{
                flex: 1,
                '& .MuiInputBase-root': {
                  height: '100%',
                  alignItems: 'flex-start',
                },
                '& .MuiInputBase-input': {
                  fontSize: '0.875rem',
                  height: '100% !important',
                  overflow: 'auto !important',
                },
              }}
              placeholder="Write your document here (Markdown supported)..."
            />
            <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
              <Button
                variant="outlined"
                size="small"
                onClick={() => {
                  // TODO: Implement markdown preview
                  console.log('Markdown preview not yet implemented');
                }}
              >
                Preview
              </Button>
              <Button
                variant="outlined"
                size="small"
                onClick={() => setDocumentContent('')}
              >
                Clear
              </Button>
            </Box>
          </Box>
        </TabPanel>
      </Box>
    </Paper>
  );
};