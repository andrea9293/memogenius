import { useState } from 'react';
import { Message } from '../types/chat';
import { chatService } from '../services/api';
import { useUser } from '../context/UserContext';
import { v4 as uuidv4 } from 'uuid';

export const useChat = () => {
  const { userId } = useUser();
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async (text: string) => {
    if (!userId) {
      console.error('User ID is required');
      return;
    }

    const userMessage: Message = {
      id: uuidv4(),
      text,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await chatService.sendMessage(text, userId);
      const botMessage: Message = {
        id: uuidv4(),
        text: response.text,
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setLoading(false);
    }
  };

  return { messages, loading, sendMessage };
};
