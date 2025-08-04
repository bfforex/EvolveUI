import React, { useState, useCallback } from 'react';
import {
  Box,
  Button,
  Typography,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
  Alert,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Switch,
  FormControlLabel,
  TextField,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  InsertDriveFile as FileIcon,
  PictureAsPdf as PdfIcon,
  Description as DocxIcon,
  Code as CodeIcon,
} from '@mui/icons-material';
import axios from 'axios';

interface FileUploadProps {
  open: boolean;
  onClose: () => void;
  onFileProcessed?: (result: any) => void;
}

interface ProcessedFile {
  filename: string;
  fileType: string;
  mimeType: string;
  sizeBytes: number;
  extractionSuccess: boolean;
  contentLength: number;
  addedToKnowledge: boolean;
  error?: string;
}

const getFileIcon = (fileType: string) => {
  switch (fileType.toLowerCase()) {
    case '.pdf':
      return <PdfIcon />;
    case '.docx':
      return <DocxIcon />;
    case '.txt':
    case '.md':
    case '.py':
    case '.js':
    case '.json':
    case '.csv':
      return <CodeIcon />;
    default:
      return <FileIcon />;
  }
};

export const FileUploadPanel: React.FC<FileUploadProps> = ({ 
  open, 
  onClose, 
  onFileProcessed 
}) => {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState<ProcessedFile[]>([]);
  const [addToKnowledge, setAddToKnowledge] = useState(true);
  const [knowledgeMetadata, setKnowledgeMetadata] = useState('');
  const [supportedTypes, setSupportedTypes] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Load supported file types when component mounts
  React.useEffect(() => {
    if (open) {
      loadSupportedTypes();
    }
  }, [open]);

  const loadSupportedTypes = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/files/supported-types');
      setSupportedTypes(response.data.supported_extensions || []);
    } catch (error) {
      console.error('Error loading supported types:', error);
      // Fallback supported types
      setSupportedTypes(['.txt', '.md', '.pdf', '.docx', '.py', '.js', '.json', '.csv']);
    }
  };

  const handleFileSelect = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    
    // Validate file types
    const validFiles = files.filter(file => {
      const extension = '.' + file.name.split('.').pop()?.toLowerCase();
      return supportedTypes.includes(extension);
    });

    const invalidFiles = files.filter(file => {
      const extension = '.' + file.name.split('.').pop()?.toLowerCase();
      return !supportedTypes.includes(extension);
    });

    if (invalidFiles.length > 0) {
      setError(`Unsupported file types: ${invalidFiles.map(f => f.name).join(', ')}`);
    } else {
      setError(null);
    }

    setSelectedFiles(validFiles);
    setResults([]);
  }, [supportedTypes]);

  const handleUpload = async () => {
    if (selectedFiles.length === 0) return;

    setUploading(true);
    setProgress(0);
    setError(null);
    const uploadResults: ProcessedFile[] = [];

    try {
      for (let i = 0; i < selectedFiles.length; i++) {
        const file = selectedFiles[i];
        const formData = new FormData();
        formData.append('file', file);
        formData.append('add_to_knowledge', addToKnowledge.toString());
        
        if (knowledgeMetadata.trim()) {
          formData.append('knowledge_metadata', knowledgeMetadata);
        }

        try {
          const response = await axios.post(
            'http://localhost:8000/api/files/upload',
            formData,
            {
              headers: {
                'Content-Type': 'multipart/form-data',
              },
            }
          );

          const result = response.data;
          uploadResults.push({
            filename: result.file_info.filename,
            fileType: result.file_info.file_type,
            mimeType: result.file_info.mime_type,
            sizeBytes: result.file_info.size_bytes,
            extractionSuccess: result.extraction.success,
            contentLength: result.extraction.content_length || 0,
            addedToKnowledge: result.knowledge_base.added,
            error: result.extraction.error
          });

          if (onFileProcessed) {
            onFileProcessed(result);
          }

        } catch (fileError: any) {
          console.error(`Error uploading ${file.name}:`, fileError);
          uploadResults.push({
            filename: file.name,
            fileType: '.' + file.name.split('.').pop()?.toLowerCase() || '',
            mimeType: 'unknown',
            sizeBytes: file.size,
            extractionSuccess: false,
            contentLength: 0,
            addedToKnowledge: false,
            error: fileError.response?.data?.detail || fileError.message
          });
        }

        setProgress(((i + 1) / selectedFiles.length) * 100);
      }

      setResults(uploadResults);
    } catch (error: any) {
      console.error('Upload error:', error);
      setError(error.response?.data?.detail || error.message);
    } finally {
      setUploading(false);
    }
  };

  const handleClose = () => {
    setSelectedFiles([]);
    setResults([]);
    setError(null);
    setProgress(0);
    setKnowledgeMetadata('');
    onClose();
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Dialog 
      open={open} 
      onClose={handleClose} 
      maxWidth="md" 
      fullWidth
      PaperProps={{
        sx: { minHeight: '60vh' }
      }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <UploadIcon />
          File Upload & Processing
        </Box>
      </DialogTitle>

      <DialogContent>
        <Box sx={{ mb: 3 }}>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Supported formats: {supportedTypes.join(', ')}
          </Typography>

          <input
            accept={supportedTypes.join(',')}
            style={{ display: 'none' }}
            id="file-upload-input"
            multiple
            type="file"
            onChange={handleFileSelect}
            disabled={uploading}
          />
          <label htmlFor="file-upload-input">
            <Button
              variant="outlined"
              component="span"
              startIcon={<UploadIcon />}
              disabled={uploading}
              fullWidth
              sx={{ mb: 2 }}
            >
              Select Files
            </Button>
          </label>

          {/* Knowledge Base Options */}
          <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={addToKnowledge}
                  onChange={(e) => setAddToKnowledge(e.target.checked)}
                  disabled={uploading}
                />
              }
              label="Add to Knowledge Base"
            />
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              When enabled, extracted text will be added to the knowledge database for RAG.
            </Typography>
            
            {addToKnowledge && (
              <TextField
                fullWidth
                size="small"
                label="Metadata (JSON)"
                placeholder='{"category": "documentation", "project": "example"}'
                value={knowledgeMetadata}
                onChange={(e) => setKnowledgeMetadata(e.target.value)}
                disabled={uploading}
                sx={{ mt: 1 }}
              />
            )}
          </Paper>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {/* Selected Files */}
          {selectedFiles.length > 0 && (
            <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>
                Selected Files ({selectedFiles.length})
              </Typography>
              <List dense>
                {selectedFiles.map((file, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      {getFileIcon('.' + file.name.split('.').pop()?.toLowerCase())}
                    </ListItemIcon>
                    <ListItemText
                      primary={file.name}
                      secondary={formatFileSize(file.size)}
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>
          )}

          {/* Upload Progress */}
          {uploading && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" sx={{ mb: 1 }}>
                Processing files... {Math.round(progress)}%
              </Typography>
              <LinearProgress variant="determinate" value={progress} />
            </Box>
          )}

          {/* Results */}
          {results.length > 0 && (
            <Paper variant="outlined" sx={{ p: 2 }}>
              <Typography variant="subtitle2" sx={{ mb: 2 }}>
                Processing Results
              </Typography>
              <List dense>
                {results.map((result, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      {getFileIcon(result.fileType)}
                    </ListItemIcon>
                    <ListItemText
                      primary={result.filename}
                      secondary={
                        <Box>
                          <Typography variant="caption" component="div">
                            {formatFileSize(result.sizeBytes)} • {result.contentLength} chars extracted
                          </Typography>
                          <Box sx={{ mt: 0.5, display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                            <Chip
                              size="small"
                              label={result.extractionSuccess ? "Extracted" : "Failed"}
                              color={result.extractionSuccess ? "success" : "error"}
                            />
                            {result.addedToKnowledge && (
                              <Chip
                                size="small"
                                label="Added to Knowledge"
                                color="info"
                              />
                            )}
                          </Box>
                          {result.error && (
                            <Typography variant="caption" color="error" component="div">
                              Error: {result.error}
                            </Typography>
                          )}
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>
          )}
        </Box>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose} disabled={uploading}>
          {results.length > 0 ? 'Close' : 'Cancel'}
        </Button>
        <Button
          onClick={handleUpload}
          variant="contained"
          disabled={selectedFiles.length === 0 || uploading}
          startIcon={<UploadIcon />}
        >
          {uploading ? 'Processing...' : 'Upload & Process'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};