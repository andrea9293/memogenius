import { TextField, IconButton, Box, Paper } from '@mui/material';
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
    <Paper
      elevation={2}
      component="form"
      onSubmit={handleSubmit}
      sx={{
        display: 'flex',
        gap: 1,
        mt: 2,
        p: 1,
        pl: 2,
        borderRadius: 3,
        boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
      }}
    >
      <TextField
        fullWidth
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Scrivi un messaggio..."
        variant="standard"
        disabled={disabled}
        InputProps={{
          disableUnderline: true,
        }}
        sx={{
          '& .MuiInputBase-root': {
            fontSize: '1rem',
            padding: '8px 0',
          }
        }}
      />
      <IconButton
        type="submit"
        color="primary"
        disabled={disabled || !message.trim()}
        sx={{
          bgcolor: message.trim() ? 'primary.main' : 'transparent',
          color: message.trim() ? 'white' : 'primary.main',
          '&:hover': {
            bgcolor: message.trim() ? 'primary.dark' : 'rgba(90,124,226,0.1)',
          },
          transition: 'all 0.2s',
          width: 44,
          height: 44,
        }}
      >
        <SendIcon />
      </IconButton>
    </Paper>
  );
};
