import { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';

interface AuthContextType {
  isAuthenticated: boolean;
  login: (accessKey: string) => Promise<boolean>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const webToken = localStorage.getItem('webToken');
    if (webToken) {
      setIsAuthenticated(true);
      api.defaults.headers.common['Authorization'] = `Bearer ${webToken}`;
    }
  }, []);

  const login = async (accessKey: string) => {
    try {
      const webToken = localStorage.getItem('webToken');
      const response = await api.post('/auth/web-login', {
        access_key: accessKey,
        web_token: webToken
      });
      
      localStorage.setItem('webToken', response.data.web_token);
      api.defaults.headers.common['Authorization'] = `Bearer ${response.data.web_token}`;
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

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
