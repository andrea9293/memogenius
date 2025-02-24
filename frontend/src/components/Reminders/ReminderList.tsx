import { List, ListItem, ListItemText, IconButton, Chip } from '@mui/material';
import { Delete as DeleteIcon, Edit as EditIcon } from '@mui/icons-material';
import { Reminder } from '../../types/reminder';

interface ReminderListProps {
  reminders: Reminder[];
  onDelete: (id: number) => void;
  onEdit: (reminder: Reminder) => void;
  loading?: boolean;
}

export const ReminderList = ({ reminders, onDelete, onEdit }: ReminderListProps) => {
  return (
    <List>
      {reminders.map((reminder) => (
        <ListItem
          key={reminder.id}
          secondaryAction={
            <>
              <IconButton edge="end" onClick={() => onEdit(reminder)}>
                <EditIcon />
              </IconButton>
              <IconButton edge="end" onClick={() => onDelete(reminder.id)}>
                <DeleteIcon />
              </IconButton>
            </>
          }
        >
          <ListItemText
            primary={reminder.text}
            secondary={new Date(reminder.due_date).toLocaleString('it-IT')}
          />
          <Chip 
            label={reminder.is_active ? 'Attivo' : 'Completato'}
            color={reminder.is_active ? 'primary' : 'default'}
            sx={{ mr: 2 }}
          />
        </ListItem>
      ))}
    </List>
  );
};
