import { Box, CircularProgress, Typography } from '@mui/material';

export const TypingIndicator = () => {
  return (
    <Box 
      sx={{ 
        display: 'flex',
        alignItems: 'center',
        gap: 1,
        p: 2,
        bgcolor: 'grey.100',
        borderRadius: 2,
        maxWidth: 'fit-content'
      }}
    >
      <CircularProgress size={20} />
      <Typography variant="body2">Neko sta scrivendo...</Typography>
    </Box>
  );
};
