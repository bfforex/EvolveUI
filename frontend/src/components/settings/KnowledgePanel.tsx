import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  TextField,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Chip,
  Paper,
  Alert,
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  Storage as StorageIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';

interface KnowledgePanelProps {
  open: boolean;
  onClose: () => void;
}

interface KnowledgeItem {
  id: string;
  content: string;
  metadata: Record<string, any>;
  distance?: number;
}

export const KnowledgePanel: React.FC<KnowledgePanelProps> = ({ open, onClose }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [newContent, setNewContent] = useState('');
  const [searchResults, setSearchResults] = useState<KnowledgeItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState({ chromadb_available: false, knowledge_documents: 0 });

  React.useEffect(() => {
    if (open) {
      fetchStatus();
    }
  }, [open]);

  const fetchStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/search/status');
      const data = await response.json();
      setStatus(data);
    } catch (error) {
      console.error('Failed to fetch status:', error);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setIsLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/search/knowledge?q=${encodeURIComponent(searchQuery)}&limit=10`
      );
      const data = await response.json();
      setSearchResults(data.results || []);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddContent = async () => {
    if (!newContent.trim()) return;
    
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/search/knowledge/add', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: newContent,
          metadata: {
            type: 'user_added',
            timestamp: new Date().toISOString(),
            source: 'manual'
          }
        }),
      });
      
      const data = await response.json();
      if (data.success) {
        setNewContent('');
        fetchStatus(); // Refresh status
        // Show success message
      }
    } catch (error) {
      console.error('Failed to add content:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatDistance = (distance?: number) => {
    if (distance === undefined) return '';
    const similarity = (1 - distance) * 100;
    return `${similarity.toFixed(1)}% similar`;
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="lg" 
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
          <StorageIcon />
          Knowledge Base Management
        </Box>
      </DialogTitle>
      
      <DialogContent>
        {/* Status */}
        <Box sx={{ mb: 3 }}>
          <Alert 
            severity={status.chromadb_available ? 'success' : 'warning'}
            sx={{ mb: 2 }}
          >
            ChromaDB Status: {status.chromadb_available ? 'Connected' : 'Not Available'} 
            {status.chromadb_available && ` • ${status.knowledge_documents} documents stored`}
          </Alert>
        </Box>

        {/* Add New Content */}
        <Paper elevation={1} sx={{ p: 2, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Add Knowledge
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-start' }}>
            <TextField
              fullWidth
              multiline
              rows={3}
              value={newContent}
              onChange={(e) => setNewContent(e.target.value)}
              placeholder="Enter knowledge content to add to the database..."
              variant="outlined"
            />
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={handleAddContent}
              disabled={!newContent.trim() || isLoading}
              sx={{ minWidth: 120 }}
            >
              Add
            </Button>
          </Box>
        </Paper>

        {/* Search */}
        <Paper elevation={1} sx={{ p: 2, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Search Knowledge
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <TextField
              fullWidth
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search the knowledge base..."
              variant="outlined"
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
            <Button
              variant="contained"
              startIcon={<SearchIcon />}
              onClick={handleSearch}
              disabled={!searchQuery.trim() || isLoading}
              sx={{ minWidth: 120 }}
            >
              Search
            </Button>
          </Box>

          {/* Search Results */}
          {searchResults.length > 0 && (
            <Box>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Found {searchResults.length} results
              </Typography>
              <List>
                {searchResults.map((item, index) => (
                  <ListItem
                    key={item.id || index}
                    sx={{
                      border: '1px solid rgba(255, 255, 255, 0.12)',
                      borderRadius: 1,
                      mb: 1,
                      bgcolor: 'background.default',
                    }}
                  >
                    <ListItemText
                      primary={
                        <Box>
                          <Typography variant="body1" sx={{ mb: 1 }}>
                            {item.content}
                          </Typography>
                          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                            {item.distance !== undefined && (
                              <Chip 
                                label={formatDistance(item.distance)} 
                                size="small" 
                                color="primary" 
                              />
                            )}
                            {item.metadata?.type && (
                              <Chip 
                                label={item.metadata.type} 
                                size="small" 
                                variant="outlined" 
                              />
                            )}
                            {item.metadata?.source && (
                              <Chip 
                                label={item.metadata.source} 
                                size="small" 
                                variant="outlined" 
                              />
                            )}
                          </Box>
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}
        </Paper>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose}>
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};