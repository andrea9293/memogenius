import { Box, Paper, Typography, useTheme } from '@mui/material';
import { Message } from '../../types/chat';
import { TypingIndicator } from './TypingIndicator';
import { useEffect, useRef } from 'react';

interface ChatWindowProps {
  messages: Message[];
  loading: boolean;
}

export const ChatWindow = ({ messages, loading }: ChatWindowProps) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const theme = useTheme();

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // Function to safely render HTML
  const createMarkup = (html: string) => {
    return { __html: html };
  };

  return (
    <Paper
      sx={{
        height: 'calc(100vh - 200px)',
        overflow: 'auto',
        p: 3,
        display: 'flex',
        flexDirection: 'column',
        gap: 2,
        borderRadius: 3,
        boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
      }}
    >
      {messages.length === 0 && !loading && (
        <Box sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100%',
          color: 'text.secondary',
          textAlign: 'center',
          p: 3
        }}>
          <Typography variant="h6" gutterBottom>
            Inizia una conversazione
          </Typography>
          <Typography variant="body2">
            Scrivi un messaggio per iniziare a chattare con MemoGenius
          </Typography>
        </Box>
      )}

      {messages.map((message) => (
        <Box
          key={message.id}
          sx={{
            alignSelf: message.sender === 'user' ? 'flex-end' : 'flex-start',
            maxWidth: '75%',
            bgcolor: message.sender === 'user' ? 'primary.main' : theme.palette.grey[100],
            color: message.sender === 'user' ? 'white' : 'text.primary',
            p: 2,
            px: 3,
            borderRadius: 3,
            borderTopRightRadius: message.sender === 'user' ? 1 : 3,
            borderTopLeftRadius: message.sender === 'user' ? 3 : 1,
            boxShadow: message.sender === 'user'
              ? '0 2px 8px rgba(90,124,226,0.2)'
              : '0 2px 8px rgba(0,0,0,0.05)',
            // Specific styles only for <pre> and <blockquote>
            '& pre': {
              backgroundColor: theme.palette.mode === 'dark' 
                ? 'rgba(0, 0, 0, 0.2)' 
                : 'rgba(0, 0, 0, 0.04)',
              padding: theme.spacing(1.5),
              borderRadius: theme.spacing(1),
              overflowX: 'auto',
              fontFamily: 'monospace',
              fontSize: '0.875rem',
              margin: theme.spacing(1, 0),
            },
            '& blockquote': {
              borderLeft: `4px solid ${theme.palette.divider}`,
              margin: theme.spacing(1, 0),
              paddingLeft: theme.spacing(2),
              opacity: 0.8,
              fontStyle: 'italic',
            },
          }}
        >
          {/* Render as HTML instead of plain text */}
          {message.sender === 'user' ? (
            <Typography variant="body1">{message.text}</Typography>
          ) : (
            <Typography 
              variant="body1" 
              component="div" 
              dangerouslySetInnerHTML={createMarkup(message.text)} 
            />
          )}
        </Box>
      ))}

      {loading && (
        <Box sx={{ alignSelf: 'flex-start' }}>
          <TypingIndicator />
        </Box>
      )}

      <div ref={messagesEndRef} />
    </Paper>
  );
};
