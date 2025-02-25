import { Box, AppBar, Toolbar, Typography, IconButton, Avatar, Drawer, List, ListItem, ListItemIcon, ListItemText, useTheme, Divider } from '@mui/material';
import { Home as HomeIcon, Chat as ChatIcon, EventNote as EventNoteIcon, Logout as LogoutIcon } from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useUser } from '../../context/UserContext';
import { ReactNode } from 'react';

interface MainLayoutProps {
  children: ReactNode;
}

export const MainLayout = ({ children }: MainLayoutProps) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { logout } = useUser();
  const theme = useTheme();

  const drawerWidth = 260;

  const menuItems = [
    { text: 'Dashboard', icon: <HomeIcon />, path: '/' },
    { text: 'Chat', icon: <ChatIcon />, path: '/chat' },
    { text: 'Promemoria', icon: <EventNoteIcon />, path: '/reminders' }
  ];

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      {/* App Bar */}
      <AppBar
        position="fixed"
        sx={{
          zIndex: theme.zIndex.drawer + 1,
          bgcolor: 'white',
          color: 'text.primary',
          boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
        }}
      >
        <Toolbar>
          <Typography variant="h5" sx={{ flexGrow: 1, fontWeight: 600, color: 'primary.main' }}>
            MemoGenius
          </Typography>

          <IconButton
            color="primary"
            onClick={handleLogout}
            sx={{ mr: 1 }}
          >
            <LogoutIcon />
          </IconButton>

          <Avatar sx={{ bgcolor: 'primary.main' }}>MG</Avatar>
        </Toolbar>
      </AppBar>

      {/* Drawer / Sidebar */}
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          ['& .MuiDrawer-paper']: {
            width: drawerWidth,
            boxSizing: 'border-box',
            bgcolor: 'background.default',
            border: 'none',
            borderRight: '1px solid',
            borderColor: 'divider',
          },
        }}
      >
        <Toolbar /> {/* Spacer to push content below AppBar */}
        <Box sx={{ overflow: 'auto', px: 2, py: 3 }}>
          {menuItems.map((item) => (
            <ListItem
              button
              key={item.text}
              onClick={() => navigate(item.path)}
              sx={{
                borderRadius: 2,
                mb: 1,
                bgcolor: location.pathname === item.path ? 'primary.light' : 'transparent',
                color: location.pathname === item.path ? 'primary.dark' : 'text.secondary',
                '&:hover': {
                  bgcolor: location.pathname === item.path ? 'primary.light' : 'rgba(0,0,0,0.04)'
                }
              }}
            >
              <ListItemIcon
                sx={{
                  color: location.pathname === item.path ? 'primary.dark' : 'text.secondary',
                  minWidth: 40
                }}
              >
                {item.icon}
              </ListItemIcon>
              <ListItemText
                primary={item.text}
                primaryTypographyProps={{
                  fontWeight: location.pathname === item.path ? 600 : 400
                }}
              />
            </ListItem>
          ))}
        </Box>
      </Drawer>

      {/* Main content */}
      <Box component="main" sx={{ flexGrow: 1, p: 3, pt: 8, overflowY: 'auto' }}>
        {children}
      </Box>
    </Box>
  );

  function handleLogout() {
    logout();
  }
};
