import { Box, CircularProgress, Typography } from '@mui/material';

export const TypingIndicator = () => {
  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 1.5,
        p: 2,
        bgcolor: 'grey.100',
        borderRadius: 3,
        borderTopLeftRadius: 1,
        maxWidth: 'fit-content',
        boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
      }}
    >
      <CircularProgress size={20} thickness={5} />
      <Typography variant="body2" fontWeight={500}>Neko sta scrivendo...</Typography>
    </Box>
  );
};
