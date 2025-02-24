import { Box, Paper, Typography } from '@mui/material';
import { Message } from '../../types/chat';
import { TypingIndicator } from './TypingIndicator';
import { useEffect, useRef } from 'react';

interface ChatWindowProps {
  messages: Message[];
  loading: boolean;
}

export const ChatWindow = ({ messages, loading }: ChatWindowProps) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  return (
    <Paper 
      sx={{ 
        height: 'calc(100vh - 200px)', 
        overflow: 'auto',
        p: 2,
        display: 'flex',
        flexDirection: 'column',
        gap: 2
      }}
    >
      {messages.map((message) => (
        <Box
          key={message.id}
          sx={{
            alignSelf: message.sender === 'user' ? 'flex-end' : 'flex-start',
            maxWidth: '70%',
            bgcolor: message.sender === 'user' ? 'primary.main' : 'grey.200',
            color: message.sender === 'user' ? 'white' : 'text.primary',
            p: 2,
            borderRadius: 2
          }}
        >
          <Typography>{message.text}</Typography>
        </Box>
      ))}
      {loading && <TypingIndicator />}
      <div ref={messagesEndRef} />
    </Paper>
  );
};