import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material';
import { MainLayout } from './components/Layout/MainLayout';
import { NotificationProvider } from './context/NotificationContext';
import { UserProvider, useUser } from './context/UserContext';
import { LoginForm } from './components/Auth/LoginForm';
import { Chat } from './pages/Chat';
import { Reminders } from './pages/Reminders';
import { Dashboard } from './pages/Dashboard';

const theme = createTheme({
  palette: {
    primary: {
      main: '#5a7ce2',
      light: '#8eacff',
      dark: '#2851b0',
    },
    secondary: {
      main: '#72baac',
      light: '#a3ecde',
      dark: '#418a7d',
    },
    background: {
      default: '#f8f9fd',
      paper: '#ffffff',
    },
    text: {
      primary: '#2a3142',
      secondary: '#6b7280',
    }
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h5: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
    subtitle1: {
      fontWeight: 500,
    }
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 12px rgba(0,0,0,0.05)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
  },
});

// Authenticated content component with proper context access
const AuthenticatedContent = () => {
  const { userId } = useUser();

  return userId ? (
    <BrowserRouter>
      <MainLayout>
        <Routes>
          <Route path="/chat" element={<Chat />} />
          <Route path="/reminders" element={<Reminders />} />
          <Route path="/" element={<Dashboard />} />
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
