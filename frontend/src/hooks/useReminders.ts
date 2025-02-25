import { useState, useEffect } from 'react';
import { Reminder, ReminderFormData } from '../types/reminder';
import { reminderService } from '../services/api';
import { useNotification } from '../context/NotificationContext';
import { useUser } from '../context/UserContext';

export const useReminders = () => {
    const { userId } = useUser();
    const [reminders, setReminders] = useState<Reminder[]>([]);
    const [loading, setLoading] = useState(false);
    const { showNotification } = useNotification();

    const fetchReminders = async () => {
        console.log('Fetching reminders for user:', userId);
        if (!userId) return;
        setLoading(true);
        try {
            const data = await reminderService.getAll(userId);
            setReminders(data);
        } catch (error) {
            console.error('Error fetching reminders:', error);
        } finally {
            setLoading(false);
        }
    };

    const createReminder = async (data: ReminderFormData) => {
        try {
          const newReminder = await reminderService.create(data, userId!);  // Passiamo userId
          setReminders(prev => [...prev, newReminder]);
          showNotification('Promemoria creato con successo', 'success');
        } catch (error) {
          showNotification('Errore durante la creazione del promemoria', 'error');
        }
    };

    const updateReminder = async (id: number, data: ReminderFormData) => {
        try {
            const updatedReminder = await reminderService.update(id, data);
            setReminders(prev =>
                prev.map(reminder =>
                    reminder.id === id ? updatedReminder : reminder
                )
            );
            showNotification('Promemoria aggiornato con successo', 'success');
        } catch (error) {
            showNotification('Errore durante l\'aggiornamento del promemoria', 'error');
        }
    };

    const deleteReminder = async (id: number) => {
        try {
            await reminderService.delete(id);
            setReminders(prev => prev.filter(reminder => reminder.id !== id));
            showNotification('Promemoria eliminato con successo', 'success');
        } catch (error) {
            showNotification('Errore durante l\'eliminazione del promemoria', 'error');
        }
    };

    useEffect(() => {
        fetchReminders();
    }, []);

    return {
        reminders,
        loading,
        createReminder,
        updateReminder,
        deleteReminder
    };
};