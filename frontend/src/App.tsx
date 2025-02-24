import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material';
import { MainLayout } from './components/Layout/MainLayout';
import { NotificationProvider } from './context/NotificationContext';
import { UserProvider, useUser } from './context/UserContext';  // Add useUser import
import { LoginForm } from './components/Auth/LoginForm';
import { Chat } from './pages/Chat';
import { Reminders } from './pages/Reminders';

const theme = createTheme({});

// Authenticated content component with proper context access
const AuthenticatedContent = () => {
  const { userId } = useUser();  // Now useUser is properly imported

  return userId ? (
    <BrowserRouter>
      <MainLayout>
        <Routes>
          <Route path="/chat" element={<Chat />} />
          <Route path="/reminders" element={<Reminders />} />
          <Route path="/" element={<Chat />} />
        </Routes>
      </MainLayout>
    </BrowserRouter>
  ) : (
    <LoginForm />
  );
};

// Main App component with providers
function App() {
  return (
    <ThemeProvider theme={theme}>
      <UserProvider>
        <NotificationProvider>
          <AuthenticatedContent />
        </NotificationProvider>
      </UserProvider>
    </ThemeProvider>
  );
}

export default App;
