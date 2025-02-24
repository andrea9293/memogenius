import { List, ListItem, ListItemIcon, ListItemText } from '@mui/material';
import { Chat as ChatIcon, EventNote as EventNoteIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

export const Sidebar = () => {
  const navigate = useNavigate();

  const menuItems = [
    { text: 'Chat', icon: <ChatIcon />, path: '/chat' },
    { text: 'Promemoria', icon: <EventNoteIcon />, path: '/reminders' }
  ];

  return (
    <List>
      {menuItems.map((item) => (
        <ListItem 
          button 
          key={item.text} 
          onClick={() => navigate(item.path)}
        >
          <ListItemIcon>{item.icon}</ListItemIcon>
          <ListItemText primary={item.text} />
        </ListItem>
      ))}
    </List>
  );
};
