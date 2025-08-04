import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Settings as SettingsIcon,
  Code as CodeIcon,
  Storage as StorageIcon,
} from '@mui/icons-material';

interface TopBarProps {
  onToggleConversations: () => void;
  onToggleWorkpad: () => void;
  onOpenSettings: () => void;
  onOpenKnowledge: () => void;
  isWorkpadOpen: boolean;
}

export const TopBar: React.FC<TopBarProps> = ({
  onToggleConversations,
  onToggleWorkpad,
  onOpenSettings,
  onOpenKnowledge,
  isWorkpadOpen,
}) => {
  return (
    <AppBar 
      position="static" 
      elevation={0}
      sx={{ 
        bgcolor: 'background.paper',
        borderBottom: '1px solid rgba(255, 255, 255, 0.12)',
      }}
    >
      <Toolbar>
        {/* Left side - Menu toggle */}
        <IconButton
          edge="start"
          color="inherit"
          aria-label="toggle conversations"
          onClick={onToggleConversations}
          sx={{ mr: 2 }}
        >
          <MenuIcon />
        </IconButton>

        {/* Center - Title */}
        <Typography 
          variant="h6" 
          component="div" 
          sx={{ 
            flexGrow: 1,
            fontWeight: 600,
            color: 'primary.main'
          }}
        >
          EvolveUI
        </Typography>

        {/* Right side - Actions */}
        <Box sx={{ display: 'flex', gap: 1 }}>
          <IconButton
            color="inherit"
            aria-label="toggle workpad"
            onClick={onToggleWorkpad}
            sx={{ 
              bgcolor: isWorkpadOpen ? 'action.selected' : 'transparent',
            }}
          >
            <CodeIcon />
          </IconButton>
          
          <IconButton
            color="inherit"
            aria-label="knowledge base"
            onClick={onOpenKnowledge}
          >
            <StorageIcon />
          </IconButton>
          
          <IconButton
            color="inherit"
            aria-label="settings"
            onClick={onOpenSettings}
          >
            <SettingsIcon />
          </IconButton>
        </Box>
      </Toolbar>
    </AppBar>
  );
};