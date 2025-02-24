import { useState } from 'react';
import { Box, TextField, Button, Dialog, DialogTitle, DialogContent, DialogActions } from '@mui/material';
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
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        {initialData ? 'Modifica Promemoria' : 'Nuovo Promemoria'}
      </DialogTitle>
      <DialogContent>
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
          <TextField
            fullWidth
            label="Testo"
            value={formData.text}
            onChange={(e) => setFormData({ ...formData, text: e.target.value })}
            margin="normal"
          />
          <TextField
            fullWidth
            type="datetime-local"
            label="Data e ora"
            value={formData.due_date}
            onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
            margin="normal"
            InputLabelProps={{ shrink: true }}
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Annulla</Button>
        <Button onClick={handleSubmit} variant="contained">
          Salva
        </Button>
      </DialogActions>
    </Dialog>
  );
};
