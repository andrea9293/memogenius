import { List, ListItem, ListItemText, IconButton, Chip, Paper, Typography, Box, Divider } from '@mui/material';
import { Delete as DeleteIcon, Edit as EditIcon } from '@mui/icons-material';
import { Reminder } from '../../types/reminder';

interface ReminderListProps {
  reminders: Reminder[];
  onDelete: (id: number) => void;
  onEdit: (reminder: Reminder) => void;
  loading?: boolean;
}

export const ReminderList = ({ reminders, onDelete, onEdit, loading }: ReminderListProps) => {
  return (
    <Paper
      elevation={2}
      sx={{
        borderRadius: 3,
        overflow: 'hidden',
        boxShadow: '0 4px 12px rgba(0,0,0,0.05)'
      }}
    >
      <Box sx={{ p: 2, pb: 1, borderBottom: '1px solid', borderColor: 'divider' }}>
        <Typography variant="h6" fontWeight={600}>I tuoi promemoria</Typography>
      </Box>

      {reminders.length === 0 && !loading ? (
        <Box sx={{ py: 5, px: 3, textAlign: 'center', color: 'text.secondary' }}>
          <Typography variant="body1">Nessun promemoria disponibile</Typography>
          <Typography variant="body2" sx={{ mt: 1 }}>
            Crea un nuovo promemoria per visualizzarlo qui
          </Typography>
        </Box>
      ) : (
        <List sx={{ py: 0 }}>
          {reminders.map((reminder, index) => (
            <Box key={reminder.id}>
              {index > 0 && <Divider component="li" />}
              <ListItem
                sx={{
                  py: 2,
                  transition: 'background-color 0.2s',
                  '&:hover': {
                    bgcolor: 'rgba(0,0,0,0.02)'
                  }
                }}
                secondaryAction={
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <IconButton
                      edge="end"
                      onClick={() => onEdit(reminder)}
                      size="small"
                      sx={{
                        color: 'primary.main',
                        '&:hover': { bgcolor: 'primary.lighter' }
                      }}
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      edge="end"
                      onClick={() => onDelete(reminder.id)}
                      size="small"
                      sx={{
                        color: 'error.main',
                        '&:hover': { bgcolor: 'error.lighter' }
                      }}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                }
              >
                <ListItemText
                  primary={
                    <Typography variant="body1" fontWeight={500}>
                      {reminder.text}
                    </Typography>
                  }
                  secondary={new Date(reminder.due_date).toLocaleString('it-IT')}
                />
                <Chip
                  label={reminder.is_active ? 'Attivo' : 'Completato'}
                  color={reminder.is_active ? 'primary' : 'default'}
                  variant={reminder.is_active ? 'filled' : 'outlined'}
                  size="small"
                  sx={{
                    mr: 2,
                    fontWeight: 500
                  }}
                />
              </ListItem>
            </Box>
          ))}
        </List>
      )}
    </Paper>
  );
};
