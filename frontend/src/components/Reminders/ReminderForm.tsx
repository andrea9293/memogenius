import { useState } from 'react';
import { Box, TextField, Button, Dialog, DialogTitle, DialogContent, DialogActions, Typography } from '@mui/material';
import { ReminderFormData } from '../../types/reminder';

interface ReminderFormProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: ReminderFormData) => void;
  initialData?: ReminderFormData;
}

export const ReminderForm = ({ open, onClose, onSubmit, initialData }: ReminderFormProps) => {
  const [formData, setFormData] = useState<ReminderFormData>(
    initialData || { text: '', due_date: '' }
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const selectedDate = new Date(formData.due_date);
    const localISOString = new Date(
      selectedDate.getTime() - selectedDate.getTimezoneOffset() * 60000
    ).toISOString();

    const formattedData = {
      ...formData,
      due_date: localISOString
    };

    onSubmit(formattedData);
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 3,
          boxShadow: '0 4px 20px rgba(0,0,0,0.15)'
        }
      }}
    >
      <DialogTitle sx={{ pb: 1 }}>
        <Typography variant="h5" fontWeight={600} color="primary.main">
          {initialData ? 'Modifica Promemoria' : 'Nuovo Promemoria'}
        </Typography>
      </DialogTitle>
      <DialogContent dividers sx={{ borderColor: 'rgba(0,0,0,0.08)' }}>
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
          <TextField
            fullWidth
            label="Testo del promemoria"
            value={formData.text}
            onChange={(e) => setFormData({ ...formData, text: e.target.value })}
            margin="normal"
            variant="outlined"
            placeholder="Inserisci qui il testo del promemoria..."
            InputProps={{
              sx: {
                borderRadius: 2
              }
            }}
          />
          <TextField
            fullWidth
            type="datetime-local"
            label="Data e ora"
            value={formData.due_date}
            onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
            margin="normal"
            InputLabelProps={{ shrink: true }}
            InputProps={{
              sx: {
                borderRadius: 2
              }
            }}
          />
        </Box>
      </DialogContent>
      <DialogActions sx={{ px: 3, py: 2, gap: 1 }}>
        <Button
          onClick={onClose}
          variant="outlined"
          sx={{
            borderRadius: 2,
            px: 3,
            textTransform: 'none',
            fontWeight: 500
          }}
        >
          Annulla
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          sx={{
            borderRadius: 2,
            px: 3,
            textTransform: 'none',
            fontWeight: 500
          }}
        >
          Salva
        </Button>
      </DialogActions>
    </Dialog>
  );
};
