import axios from 'axios';
import { ReminderFormData } from '../types/reminder';

export const api = axios.create({
  baseURL: '/api'
});

export const chatService = {
  sendMessage: async (message: string) => {
    const webToken = localStorage.getItem('webToken');
    const response = await api.post('/chat/message', { 
      message 
    }, {
      params: {
        user_id: webToken
      }
    });
    return response.data;
  }
};

export const reminderService = {
  getAll: async () => {
    const webToken = localStorage.getItem('webToken');
    const response = await api.get('/reminders/', {
      params: {
        user_id: webToken,
        skip: 0,
        limit: 100
      }
    });
    return response.data;
  },

  create: async (data: ReminderFormData) => {
    const webToken = localStorage.getItem('webToken');
    const response = await api.post('/reminders/', {
      ...data,
      user_id: webToken
    });
    return response.data;
  },

  update: async (id: number, data: ReminderFormData) => {
    const webToken = localStorage.getItem('webToken');
    const response = await api.put(`/reminders/${id}`, {
      ...data,
      user_id: webToken
    });
    return response.data;
  },

  delete: async (id: number) => {
    const webToken = localStorage.getItem('webToken');
    const response = await api.delete(`/reminders/${id}`, {
      params: {
        user_id: webToken
      }
    });
    return response.data;
  }
};
