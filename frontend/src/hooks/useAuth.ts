import { useState, useRef } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { api } from '../services/api';

export const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const webToken = useRef(localStorage.getItem('webToken') || uuidv4());

  const login = async (accessKey: string) => {
    try {
      const response = await api.post('/auth/web-login', {
        access_key: accessKey,
        web_token: webToken.current
      });

      // Salva il token e configura l'header per le future richieste
      localStorage.setItem('webToken', webToken.current);
      api.defaults.headers.common['Authorization'] = `Bearer ${webToken.current}`;
      
      setIsAuthenticated(true);
      return true;
    } catch (error) {
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('webToken');
    delete api.defaults.headers.common['Authorization'];
    setIsAuthenticated(false);
  };

  return { 
    isAuthenticated, 
    login, 
    logout,
    webToken: webToken.current 
  };
};
