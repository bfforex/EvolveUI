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
} from '@mui/material';
import {
  Close as CloseIcon,
  Code as CodeIcon,
  Description as DocumentIcon,
  Download as DownloadIcon,
  Upload as UploadIcon,
} from '@mui/icons-material';

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

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
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
            <Typography variant="subtitle2" sx={{ mb: 1, color: 'text.secondary' }}>
              Code Editor
            </Typography>
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
                variant="outlined"
                size="small"
                onClick={() => {
                  // TODO: Implement code execution
                  console.log('Code execution not yet implemented');
                }}
              >
                Run Code
              </Button>
              <Button
                variant="outlined"
                size="small"
                onClick={() => setCodeContent('')}
              >
                Clear
              </Button>
            </Box>
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