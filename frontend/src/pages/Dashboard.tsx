import { useState } from 'react';
import {
    Box,
    Typography,
    Grid,
    Paper,
    Button,
    List,
    ListItem,
    Divider,
    Chip,
    CircularProgress
} from '@mui/material';
import { Add as AddIcon, ArrowForward as ArrowForwardIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { ReminderForm } from '../components/Reminders/ReminderForm';
import { MessageInput } from '../components/Chat/MessageInput';
import { ReminderFormData } from '../types/reminder';
import { useReminders } from '../hooks/useReminders';
import { useChat } from '../hooks/useChat';

export const Dashboard = () => {
    const navigate = useNavigate();
    const { reminders, loading, createReminder } = useReminders();
    const { sendMessage } = useChat();
    const [isReminderFormOpen, setIsReminderFormOpen] = useState(false);

    // Mostra solo gli ultimi 3 promemoria nella dashboard
    const recentReminders = reminders.slice(0, 3);

    const handleQuickMessage = (message: string) => {
        // Invia il messaggio tramite il servizio reale
        sendMessage(message);
        // Naviga alla pagina di chat
        navigate('/chat');
    };

    const handleAddReminder = (data: ReminderFormData) => {
        createReminder(data);
        setIsReminderFormOpen(false);
    };

    return (
        <Box sx={{ height: '100%', overflow: 'auto', py: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 4 }}>
                <Typography variant="h4" fontWeight={600} color="text.primary">
                    Dashboard
                </Typography>
            </Box>

            <Grid container spacing={3} sx={{ mb: 6 }}>
                {/* Sezione promemoria */}
                <Grid item xs={12} md={6}>
                    <Paper
                        elevation={0}
                        sx={{
                            p: 3,
                            height: '100%',
                            borderRadius: 3,
                            border: '1px solid',
                            borderColor: 'grey.200',
                            boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
                            display: 'flex',
                            flexDirection: 'column'
                        }}
                    >
                        <Box sx={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            mb: 2
                        }}>
                            <Typography variant="h6" fontWeight={600}>
                                Promemoria recenti
                            </Typography>
                            <Button
                                startIcon={<AddIcon />}
                                variant="outlined"
                                size="small"
                                onClick={() => setIsReminderFormOpen(true)}
                                sx={{
                                    borderRadius: 2,
                                    textTransform: 'none'
                                }}
                            >
                                Nuovo
                            </Button>
                        </Box>

                        {loading ? (
                            <Box sx={{ py: 4, display: 'flex', justifyContent: 'center' }}>
                                <CircularProgress size={30} />
                            </Box>
                        ) : recentReminders.length === 0 ? (
                            <Box sx={{ py: 4, textAlign: 'center', color: 'text.secondary' }}>
                                <Typography variant="body1">Nessun promemoria disponibile</Typography>
                                <Typography variant="body2" sx={{ mt: 1 }}>
                                    Crea un nuovo promemoria per visualizzarlo qui
                                </Typography>
                            </Box>
                        ) : (
                            <>
                                <List sx={{ py: 0 }}>
                                    {recentReminders.map((reminder, index) => (
                                        <Box key={reminder.id}>
                                            {index > 0 && <Divider />}
                                            <ListItem
                                                sx={{
                                                    py: 2,
                                                    px: 0,
                                                    display: 'flex',
                                                    flexDirection: 'column',
                                                    alignItems: 'flex-start'
                                                }}
                                            >
                                                <Box sx={{ display: 'flex', width: '100%', mb: 1 }}>
                                                    <Typography variant="body1" fontWeight={500} sx={{ flex: 1 }}>
                                                        {reminder.text}
                                                    </Typography>
                                                    <Chip
                                                        label={reminder.is_active ? 'Attivo' : 'Completato'}
                                                        color={reminder.is_active ? 'primary' : 'default'}
                                                        size="small"
                                                        sx={{ ml: 1 }}
                                                    />
                                                </Box>
                                                <Typography variant="body2" color="text.secondary">
                                                    {new Date(reminder.due_date).toLocaleString('it-IT')}
                                                </Typography>
                                            </ListItem>
                                        </Box>
                                    ))}
                                </List>
                                <Button
                                    endIcon={<ArrowForwardIcon />}
                                    sx={{
                                        mt: 'auto',
                                        alignSelf: 'flex-end',
                                        textTransform: 'none'
                                    }}
                                    onClick={() => navigate('/reminders')}
                                >
                                    Vedi tutti
                                </Button>
                            </>
                        )}
                    </Paper>
                </Grid>

                {/* Sezione chat rapida */}
                <Grid item xs={12} md={6}>
                    <Paper
                        elevation={0}
                        sx={{
                            p: 3,
                            height: '100%',
                            borderRadius: 3,
                            border: '1px solid',
                            borderColor: 'grey.200',
                            boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
                            display: 'flex',
                            flexDirection: 'column'
                        }}
                    >
                        <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
                            Chat rapida
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                            Invia un messaggio rapido a MemoGenius
                        </Typography>

                        <Box sx={{ mt: 'auto' }}>
                            <MessageInput onSendMessage={handleQuickMessage} />
                        </Box>
                    </Paper>
                </Grid>

            </Grid>
            {/* Spazio per future funzionalità (To-do) */}
            <Box sx={{ mt: 10 }}>
                <Paper
                    elevation={0}
                    sx={{
                        p: 3,
                        borderRadius: 3,
                        border: '2px dashed',
                        borderColor: 'primary.main',
                        boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        py: 6,
                        bgcolor: 'rgba(90,124,226,0.1)',
                    }}
                >
                    <Typography variant="h6" fontWeight={600} color="primary.dark" sx={{ mb: 1 }}>
                        Funzionalità in arrivo
                    </Typography>
                    <Typography variant="body1" color="text.secondary" align="center">
                        Presto sarà disponibile una sezione per gestire i tuoi to-do e molto altro!
                    </Typography>
                </Paper>
            </Box>
            {/* Form per aggiungere un nuovo promemoria */}
            <ReminderForm
                open={isReminderFormOpen}
                onClose={() => setIsReminderFormOpen(false)}
                onSubmit={handleAddReminder}
            />
        </Box>
    );
};
