import { useState } from 'react';
import { Box, Button, Typography, CircularProgress } from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import { ReminderList } from '../components/Reminders/ReminderList';
import { ReminderForm } from '../components/Reminders/ReminderForm';
import { useReminders } from '../hooks/useReminders';
import { Reminder, ReminderFormData } from '../types/reminder';

export const Reminders = () => {
  const { reminders, loading, createReminder, updateReminder, deleteReminder } = useReminders();
  const [formOpen, setFormOpen] = useState(false);
  const [editingReminder, setEditingReminder] = useState<Reminder | null>(null);

  // Aggiungiamo un console.log per debug
  console.log('Reminders:', reminders);

  const handleCreate = (data: ReminderFormData) => {
    createReminder(data);
    setFormOpen(false);
  };

  const handleEdit = (data: ReminderFormData) => {
    if (editingReminder) {
      updateReminder(editingReminder.id, data);
      setFormOpen(false);
      setEditingReminder(null);
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h5">I miei promemoria</Typography>
        <Button 
          variant="contained" 
          startIcon={<AddIcon />}
          onClick={() => setFormOpen(true)}
        >
          Nuovo promemoria
        </Button>
      </Box>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      ) : (
        <ReminderList 
          reminders={reminders}
          onDelete={deleteReminder}
          onEdit={(reminder) => {
            setEditingReminder(reminder);
            setFormOpen(true);
          }}
        />
      )}

      <ReminderForm
        open={formOpen}
        onClose={() => {
          setFormOpen(false);
          setEditingReminder(null);
        }}
        onSubmit={editingReminder ? handleEdit : handleCreate}
        initialData={editingReminder || undefined}
      />
    </Box>
  );
};