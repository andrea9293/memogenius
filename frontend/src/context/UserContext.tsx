import { createContext, useContext, useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { api } from '../services/api';

interface UserContextType {
  userId: number | null;
  webToken: string | null;
  login: (accessKey: string) => Promise<boolean>;
  logout: () => void;
}

const UserContext = createContext<UserContextType | null>(null);

export const UserProvider = ({ children }: { children: React.ReactNode }) => {
  const [userId, setUserId] = useState<number | null>(null);
  const [webToken, setWebToken] = useState<string | null>(null);

  useEffect(() => {
    const storedToken = localStorage.getItem('webToken');
    if (!storedToken) {
      const newToken = uuidv4();
      localStorage.setItem('webToken', newToken);
      setWebToken(newToken);
    } else {
      setWebToken(storedToken);
    }
  }, []);

  const login = async (accessKey: string) => {
    try {
      const response = await api.post('/auth/web-login', {
        access_key: accessKey,
        web_token: webToken
      });
      
      // Set authorization header for future requests
      api.defaults.headers.common['Authorization'] = `Bearer ${webToken}`;
      setUserId(response.data.id);
      return true;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };

  const logout = () => {
    setUserId(null);
    localStorage.removeItem('webToken');
    delete api.defaults.headers.common['Authorization'];
  };

  return (
    <UserContext.Provider value={{ userId, webToken, login, logout }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};
