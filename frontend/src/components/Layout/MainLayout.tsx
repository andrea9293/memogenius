import { Box, AppBar, Toolbar, Typography, IconButton, Button } from '@mui/material';
import { Chat as ChatIcon, EventNote as EventNoteIcon, Logout as LogoutIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../context/UserContext';

interface MainLayoutProps {
  children: React.ReactNode;
}

export const MainLayout = ({ children }: MainLayoutProps) => {
  const navigate = useNavigate();
  const { logout } = useUser();

  const handleLogout = () => {
    logout();
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            MemoGenius
          </Typography>
          
          <IconButton color="inherit" onClick={() => navigate('/chat')}>
            <ChatIcon />
          </IconButton>
          
          <IconButton color="inherit" onClick={() => navigate('/reminders')}>
            <EventNoteIcon />
          </IconButton>
          
          <IconButton color="inherit" onClick={handleLogout}>
            <LogoutIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        {children}
      </Box>
    </Box>
  );
};
