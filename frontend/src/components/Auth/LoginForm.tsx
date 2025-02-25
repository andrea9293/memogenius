import { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  CircularProgress,
  Container,
  useTheme
} from '@mui/material';
import { useUser } from '../../context/UserContext';
import { useNotification } from '../../context/NotificationContext';

export const LoginForm = () => {
  const [accessKey, setAccessKey] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useUser();
  const { showNotification } = useNotification();
  const theme = useTheme();

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
        bgcolor: 'background.default',
        backgroundImage: `radial-gradient(at 50% 0%, ${theme.palette.primary.light}40 0%, transparent 70%)`,
      }}
    >
      <Container maxWidth="sm">
        <Paper
          component="form"
          onSubmit={handleSubmit}
          elevation={3}
          sx={{
            p: 4,
            display: 'flex',
            flexDirection: 'column',
            gap: 3,
            borderRadius: 3,
          }}
        >
          <Box sx={{ textAlign: 'center', mb: 2 }}>
            <Typography variant="h4" component="h1" fontWeight={700} color="primary.main" gutterBottom>
              MemoGenius
            </Typography>
            <Typography variant="h6" component="h2" gutterBottom sx={{ fontWeight: 500 }}>
              Accedi alla tua area personale
            </Typography>
          </Box>

          <Typography variant="body1" color="text.secondary" gutterBottom>
            Inserisci la chiave di accesso ricevuta dal bot Telegram
          </Typography>

          <TextField
            fullWidth
            label="Chiave di accesso"
            value={accessKey}
            onChange={(e) => setAccessKey(e.target.value)}
            disabled={loading}
            placeholder="MG-XXXX-XXXX"
            variant="outlined"
            InputProps={{
              sx: { borderRadius: 2 }
            }}
          />

          <Button
            fullWidth
            variant="contained"
            type="submit"
            disabled={loading || !accessKey}
            sx={{
              py: 1.5,
              mt: 1,
              borderRadius: 2,
              textTransform: 'none',
              fontWeight: 600,
              fontSize: '1rem'
            }}
          >
            {loading ? <CircularProgress size={24} color="inherit" /> : 'Accedi'}
          </Button>

          <Typography variant="body2" color="text.secondary" textAlign="center" sx={{ mt: 2 }}>
            Non hai una chiave? Avvia il bot Telegram <strong>@MemoGenius_bot</strong>
          </Typography>
        </Paper>
      </Container>
    </Box>
  );
};
