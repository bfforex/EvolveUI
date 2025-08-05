import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Paper,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
} from '@mui/material';
import {
  PlayArrow as RunIcon,
  Code as CodeIcon,
  Terminal as TerminalIcon,
} from '@mui/icons-material';

interface CodeExecutionDialogProps {
  open: boolean;
  onClose: () => void;
  initialCode?: string;
  initialLanguage?: string;
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
      id={`code-tabpanel-${index}`}
      aria-labelledby={`code-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 2 }}>{children}</Box>}
    </div>
  );
}

export const CodeExecutionDialog: React.FC<CodeExecutionDialogProps> = ({
  open,
  onClose,
  initialCode = '',
  initialLanguage = 'python',
}) => {
  const [code, setCode] = useState(initialCode);
  const [language, setLanguage] = useState(initialLanguage);
  const [isExecuting, setIsExecuting] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [tabValue, setTabValue] = useState(0);

  const supportedLanguages = [
    { value: 'python', label: 'Python' },
    { value: 'javascript', label: 'JavaScript' },
    { value: 'bash', label: 'Bash' },
  ];

  const handleExecute = async () => {
    if (!code.trim()) return;

    setIsExecuting(true);
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/api/search/code/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code,
          language,
          timeout: 30,
        }),
      });

      const data = await response.json();
      setResult(data);
      setTabValue(1); // Switch to output tab
    } catch (error) {
      setResult({
        success: false,
        error: 'Network error: Could not connect to code execution service',
      });
    } finally {
      setIsExecuting(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleClose = () => {
    setCode(initialCode);
    setLanguage(initialLanguage);
    setResult(null);
    setTabValue(0);
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <CodeIcon />
          Code Execution Environment
        </Box>
      </DialogTitle>

      <DialogContent sx={{ p: 0, height: '70vh' }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
          {/* Language Selection */}
          <Box sx={{ p: 2, borderBottom: '1px solid rgba(255, 255, 255, 0.12)' }}>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Language</InputLabel>
              <Select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                label="Language"
              >
                {supportedLanguages.map((lang) => (
                  <MenuItem key={lang.value} value={lang.value}>
                    {lang.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>

          {/* Tabs */}
          <Box sx={{ borderBottom: '1px solid rgba(255, 255, 255, 0.12)' }}>
            <Tabs value={tabValue} onChange={handleTabChange}>
              <Tab label="Code Editor" />
              <Tab label="Output" disabled={!result} />
            </Tabs>
          </Box>

          {/* Tab Content */}
          <Box sx={{ flex: 1, overflow: 'hidden' }}>
            <TabPanel value={tabValue} index={0}>
              <Box sx={{ height: 'calc(70vh - 120px)', p: 2 }}>
                <TextField
                  multiline
                  fullWidth
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  placeholder={`Enter your ${language} code here...`}
                  variant="outlined"
                  sx={{
                    height: '100%',
                    '& .MuiInputBase-root': {
                      height: '100%',
                      alignItems: 'flex-start',
                      fontFamily: 'Monaco, Consolas, "Courier New", monospace',
                      fontSize: '0.875rem',
                    },
                    '& .MuiInputBase-input': {
                      height: '100% !important',
                      overflow: 'auto !important',
                    },
                  }}
                />
              </Box>
            </TabPanel>

            <TabPanel value={tabValue} index={1}>
              <Box sx={{ height: 'calc(70vh - 120px)', p: 2, overflow: 'auto' }}>
                {result ? (
                  <Box>
                    {result.success ? (
                      <Box>
                        <Alert severity="success" sx={{ mb: 2 }}>
                          Code executed successfully in {result.execution_time?.toFixed(3)}s
                        </Alert>

                        {result.stdout && (
                          <Box sx={{ mb: 2 }}>
                            <Typography variant="subtitle2" gutterBottom>
                              Output:
                            </Typography>
                            <Paper
                              elevation={1}
                              sx={{
                                p: 2,
                                bgcolor: 'background.default',
                                fontFamily: 'Monaco, Consolas, "Courier New", monospace',
                                fontSize: '0.875rem',
                                whiteSpace: 'pre-wrap',
                                overflow: 'auto',
                                maxHeight: '200px',
                              }}
                            >
                              {result.stdout}
                            </Paper>
                          </Box>
                        )}

                        {result.stderr && (
                          <Box sx={{ mb: 2 }}>
                            <Typography variant="subtitle2" gutterBottom color="warning.main">
                              Errors/Warnings:
                            </Typography>
                            <Paper
                              elevation={1}
                              sx={{
                                p: 2,
                                bgcolor: 'background.default',
                                fontFamily: 'Monaco, Consolas, "Courier New", monospace',
                                fontSize: '0.875rem',
                                whiteSpace: 'pre-wrap',
                                overflow: 'auto',
                                maxHeight: '200px',
                                border: '1px solid',
                                borderColor: 'warning.main',
                              }}
                            >
                              {result.stderr}
                            </Paper>
                          </Box>
                        )}

                        <Typography variant="caption" color="text.secondary">
                          Return code: {result.return_code} | Language: {result.language}
                        </Typography>
                      </Box>
                    ) : (
                      <Alert severity="error">
                        <Typography variant="subtitle2" gutterBottom>
                          Execution failed:
                        </Typography>
                        <Typography variant="body2">
                          {result.error}
                        </Typography>
                      </Alert>
                    )}
                  </Box>
                ) : (
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      height: '100%',
                      color: 'text.secondary',
                    }}
                  >
                    <Box sx={{ textAlign: 'center' }}>
                      <TerminalIcon sx={{ fontSize: 64, mb: 2, opacity: 0.5 }} />
                      <Typography>
                        Execute code to see output here
                      </Typography>
                    </Box>
                  </Box>
                )}
              </Box>
            </TabPanel>
          </Box>
        </Box>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose}>Close</Button>
        <Button
          onClick={handleExecute}
          variant="contained"
          disabled={!code.trim() || isExecuting}
          startIcon={isExecuting ? <CircularProgress size={16} /> : <RunIcon />}
        >
          {isExecuting ? 'Executing...' : 'Run Code'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};