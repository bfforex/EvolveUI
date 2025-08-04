import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  IconButton,
  Menu,
  MenuItem,
  Divider,
} from '@mui/material';
import {
  MoreVert as MoreVertIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { formatDistanceToNow } from 'date-fns';

interface Conversation {
  id: string;
  title: string;
  messages: any[];
  created_at: string;
  updated_at: string;
}

interface ConversationPanelProps {
  isOpen: boolean;
  selectedConversationId: string | null;
  onSelectConversation: (id: string) => void;
}

export const ConversationPanel: React.FC<ConversationPanelProps> = ({
  isOpen,
  selectedConversationId,
  onSelectConversation,
}) => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedForMenu, setSelectedForMenu] = useState<string | null>(null);

  // Load conversations from backend
  useEffect(() => {
    fetchConversations();
  }, []);

  const fetchConversations = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/conversations/');
      const data = await response.json();
      setConversations(data.conversations || []);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    }
  };

  const createNewConversation = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/conversations/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: 'New Conversation'
        }),
      });
      const data = await response.json();
      if (data.conversation) {
        setConversations(prev => [data.conversation, ...prev]);
        onSelectConversation(data.conversation.id);
      }
    } catch (error) {
      console.error('Failed to create conversation:', error);
    }
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, conversationId: string) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
    setSelectedForMenu(conversationId);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedForMenu(null);
  };

  const deleteConversation = async (conversationId: string) => {
    try {
      await fetch(`http://localhost:8000/api/conversations/${conversationId}`, {
        method: 'DELETE',
      });
      setConversations(prev => prev.filter(conv => conv.id !== conversationId));
      if (selectedConversationId === conversationId) {
        onSelectConversation('');
      }
    } catch (error) {
      console.error('Failed to delete conversation:', error);
    }
    handleMenuClose();
  };

  // Group conversations by time
  const groupConversationsByTime = (conversations: Conversation[]) => {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000);
    const thisWeek = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
    const lastWeek = new Date(today.getTime() - 14 * 24 * 60 * 60 * 1000);

    const groups = {
      today: [] as Conversation[],
      yesterday: [] as Conversation[],
      thisWeek: [] as Conversation[],
      lastWeek: [] as Conversation[],
      older: [] as Conversation[],
    };

    conversations.forEach(conv => {
      const updatedAt = new Date(conv.updated_at);
      if (updatedAt >= today) {
        groups.today.push(conv);
      } else if (updatedAt >= yesterday) {
        groups.yesterday.push(conv);
      } else if (updatedAt >= thisWeek) {
        groups.thisWeek.push(conv);
      } else if (updatedAt >= lastWeek) {
        groups.lastWeek.push(conv);
      } else {
        groups.older.push(conv);
      }
    });

    return groups;
  };

  const groupedConversations = groupConversationsByTime(conversations);

  if (!isOpen) {
    return null;
  }

  return (
    <Paper
      elevation={1}
      sx={{
        width: 320,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: 'background.paper',
        borderRight: '1px solid rgba(255, 255, 255, 0.12)',
      }}
    >
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: '1px solid rgba(255, 255, 255, 0.12)' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Conversations
          </Typography>
          <IconButton size="small" onClick={createNewConversation}>
            <AddIcon />
          </IconButton>
        </Box>
      </Box>

      {/* Conversation List */}
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        {Object.entries(groupedConversations).map(([groupName, groupConversations]) => {
          if (groupConversations.length === 0) return null;
          
          const groupLabels = {
            today: 'Today',
            yesterday: 'Yesterday',
            thisWeek: 'This Week',
            lastWeek: 'Last Week',
            older: 'Older',
          };

          return (
            <Box key={groupName}>
              <Typography
                variant="caption"
                sx={{
                  px: 2,
                  py: 1,
                  display: 'block',
                  color: 'text.secondary',
                  fontWeight: 600,
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px',
                }}
              >
                {groupLabels[groupName as keyof typeof groupLabels]}
              </Typography>
              <List dense>
                {groupConversations.map((conversation) => (
                  <ListItem
                    key={conversation.id}
                    disablePadding
                    secondaryAction={
                      <IconButton
                        edge="end"
                        size="small"
                        onClick={(e) => handleMenuClick(e, conversation.id)}
                      >
                        <MoreVertIcon fontSize="small" />
                      </IconButton>
                    }
                  >
                    <ListItemButton
                      selected={selectedConversationId === conversation.id}
                      onClick={() => onSelectConversation(conversation.id)}
                      sx={{ pr: 6 }}
                    >
                      <ListItemText
                        primary={conversation.title}
                        secondary={formatDistanceToNow(new Date(conversation.updated_at), { addSuffix: true })}
                        primaryTypographyProps={{
                          sx: {
                            fontSize: '0.875rem',
                            fontWeight: selectedConversationId === conversation.id ? 600 : 400,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                          }
                        }}
                        secondaryTypographyProps={{
                          sx: { fontSize: '0.75rem' }
                        }}
                      />
                    </ListItemButton>
                  </ListItem>
                ))}
              </List>
              <Divider sx={{ mx: 2 }} />
            </Box>
          );
        })}
      </Box>

      {/* Context Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => {/* TODO: Implement rename */}}>
          Rename
        </MenuItem>
        <MenuItem onClick={() => {/* TODO: Implement archive */}}>
          Archive
        </MenuItem>
        <MenuItem 
          onClick={() => selectedForMenu && deleteConversation(selectedForMenu)}
          sx={{ color: 'error.main' }}
        >
          Delete
        </MenuItem>
      </Menu>
    </Paper>
  );
};