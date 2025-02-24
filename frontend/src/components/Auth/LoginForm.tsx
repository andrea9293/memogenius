import { useState } from 'react';
import { 
  Box, 
  TextField, 
  Button, 
  Typography, 
  Paper,
  CircularProgress 
} from '@mui/material';
import { useUser } from '../../context/UserContext';
import { useNotification } from '../../context/NotificationContext';

export const LoginForm = () => {
  const [accessKey, setAccessKey] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useUser();
  const { showNotification } = useNotification();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const success = await login(accessKey);
      if (success) {
        showNotification('Login effettuato con successo', 'success');
      } else {
        showNotification('Chiave di accesso non valida', 'error');
      }
    } catch (error) {
      showNotification('Errore durante il login', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box 
      sx={{ 
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'grey.100'
      }}
    >
      <Paper 
        component="form"
        onSubmit={handleSubmit}
        sx={{
          p: 4,
          maxWidth: 400,
          width: '90%',
          display: 'flex',
          flexDirection: 'column',
          gap: 2
        }}
      >
        <Typography variant="h5" component="h1" gutterBottom>
          Accedi a MemoGenius
        </Typography>

        <Typography variant="body2" color="text.secondary" gutterBottom>
          Inserisci la chiave di accesso ricevuta dal bot Telegram
        </Typography>

        <TextField
          fullWidth
          label="Chiave di accesso"
          value={accessKey}
          onChange={(e) => setAccessKey(e.target.value)}
          disabled={loading}
          placeholder="MG-XXXX-XXXX"
        />

        <Button 
          fullWidth 
          variant="contained" 
          type="submit"
          disabled={loading || !accessKey}
          sx={{ mt: 2 }}
        >
          {loading ? <CircularProgress size={24} /> : 'Accedi'}
        </Button>

        <Typography variant="body2" color="text.secondary" textAlign="center">
          Non hai una chiave? Avvia il bot Telegram @MemoGenius_bot
        </Typography>
      </Paper>
    </Box>
  );
};
