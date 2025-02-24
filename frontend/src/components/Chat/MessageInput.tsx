import { TextField, IconButton, Box } from '@mui/material';
import { Send as SendIcon } from '@mui/icons-material';
import { useState } from 'react';

interface MessageInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
}

export const MessageInput = ({ onSendMessage, disabled }: MessageInputProps) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim()) {
      onSendMessage(message);
      setMessage('');
    }
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      sx={{ 
        display: 'flex', 
        gap: 1,
        mt: 2
      }}
    >
      <TextField
        fullWidth
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Scrivi un messaggio..."
        variant="outlined"
        disabled={disabled}
      />
      <IconButton 
        type="submit" 
        color="primary"
        disabled={disabled}
      >
        <SendIcon />
      </IconButton>
    </Box>
  );
};