import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  LinearProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Delete as DeleteIcon,
  InsertDriveFile as FileIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';

interface FileUploadDialogProps {
  open: boolean;
  onClose: () => void;
  onUploadComplete?: (results: any[]) => void;
}

interface UploadedFile {
  file: File;
  status: 'pending' | 'uploading' | 'success' | 'error';
  result?: any;
  error?: string;
  progress?: number;
}

export const FileUploadDialog: React.FC<FileUploadDialogProps> = ({
  open,
  onClose,
  onUploadComplete,
}) => {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    const newFiles = files.map(file => ({
      file,
      status: 'pending' as const,
      progress: 0,
    }));
    setUploadedFiles(prev => [...prev, ...newFiles]);
  };

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const uploadFiles = async () => {
    setIsUploading(true);
    const results = [];

    for (let i = 0; i < uploadedFiles.length; i++) {
      const fileData = uploadedFiles[i];
      if (fileData.status !== 'pending') continue;

      // Update status to uploading
      setUploadedFiles(prev => prev.map((f, index) => 
        index === i ? { ...f, status: 'uploading', progress: 0 } : f
      ));

      try {
        const formData = new FormData();
        formData.append('file', fileData.file);

        const response = await fetch('http://localhost:8000/api/search/files/upload', {
          method: 'POST',
          body: formData,
        });

        const result = await response.json();

        if (result.success) {
          setUploadedFiles(prev => prev.map((f, index) => 
            index === i ? { ...f, status: 'success', result, progress: 100 } : f
          ));
          results.push(result);
        } else {
          setUploadedFiles(prev => prev.map((f, index) => 
            index === i ? { ...f, status: 'error', error: result.error || 'Upload failed' } : f
          ));
        }
      } catch (error) {
        setUploadedFiles(prev => prev.map((f, index) => 
          index === i ? { ...f, status: 'error', error: 'Network error' } : f
        ));
      }
    }

    setIsUploading(false);
    if (results.length > 0 && onUploadComplete) {
      onUploadComplete(results);
    }
  };

  const handleClose = () => {
    if (!isUploading) {
      setUploadedFiles([]);
      onClose();
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <SuccessIcon color="success" />;
      case 'error':
        return <ErrorIcon color="error" />;
      default:
        return <FileIcon />;
    }
  };

  const pendingFiles = uploadedFiles.filter(f => f.status === 'pending').length;
  const canUpload = pendingFiles > 0 && !isUploading;

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>Upload Files to Knowledge Base</DialogTitle>
      
      <DialogContent>
        <Box sx={{ mb: 3 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Upload text files, documents, and code files to add them to your knowledge base.
            Supported formats: TXT, MD, JSON, HTML, CSS, JS, TS, PY, XML, CSV
          </Typography>
        </Box>

        {/* File Selection */}
        <Box
          sx={{
            border: '2px dashed',
            borderColor: 'primary.main',
            borderRadius: 2,
            p: 3,
            textAlign: 'center',
            mb: 3,
            cursor: 'pointer',
            '&:hover': {
              bgcolor: 'rgba(25, 118, 210, 0.05)',
            },
          }}
          component="label"
        >
          <input
            type="file"
            multiple
            accept=".txt,.md,.json,.html,.css,.js,.ts,.py,.xml,.csv"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
            disabled={isUploading}
          />
          <UploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
          <Typography variant="h6" gutterBottom>
            Click to select files
          </Typography>
          <Typography variant="body2" color="text.secondary">
            or drag and drop files here
          </Typography>
        </Box>

        {/* File List */}
        {uploadedFiles.length > 0 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Selected Files ({uploadedFiles.length})
            </Typography>
            <List>
              {uploadedFiles.map((fileData, index) => (
                <ListItem key={index} sx={{ px: 0 }}>
                  <ListItemIcon>
                    {getStatusIcon(fileData.status)}
                  </ListItemIcon>
                  <ListItemText
                    primary={fileData.file.name}
                    secondary={
                      <Box>
                        <Typography variant="caption" display="block">
                          {(fileData.file.size / 1024).toFixed(1)} KB
                        </Typography>
                        {fileData.status === 'uploading' && (
                          <LinearProgress 
                            variant="indeterminate" 
                            sx={{ mt: 0.5, width: '100%' }} 
                          />
                        )}
                        {fileData.status === 'success' && fileData.result && (
                          <Alert severity="success" sx={{ mt: 0.5 }}>
                            Uploaded successfully! 
                            {fileData.result.stored_in_knowledge_base 
                              ? ' Added to knowledge base.' 
                              : ' (Knowledge base not available)'}
                          </Alert>
                        )}
                        {fileData.status === 'error' && (
                          <Alert severity="error" sx={{ mt: 0.5 }}>
                            {fileData.error}
                          </Alert>
                        )}
                      </Box>
                    }
                  />
                  {fileData.status === 'pending' && (
                    <IconButton 
                      onClick={() => removeFile(index)}
                      disabled={isUploading}
                      size="small"
                    >
                      <DeleteIcon />
                    </IconButton>
                  )}
                </ListItem>
              ))}
            </List>
          </Box>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose} disabled={isUploading}>
          {uploadedFiles.some(f => f.status === 'success') ? 'Done' : 'Cancel'}
        </Button>
        <Button 
          onClick={uploadFiles} 
          variant="contained" 
          disabled={!canUpload}
          startIcon={<UploadIcon />}
        >
          Upload {pendingFiles > 0 ? `${pendingFiles} file${pendingFiles !== 1 ? 's' : ''}` : 'Files'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};