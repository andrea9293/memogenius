import { Box } from '@mui/material';
import { ChatWindow } from '../components/Chat/ChatWindow';
import { MessageInput } from '../components/Chat/MessageInput';
import { useChat } from '../hooks/useChat';

export const Chat = () => {
  const { messages, loading, sendMessage } = useChat();

  return (
    <Box sx={{ height: '100%' }}>
      <ChatWindow messages={messages} loading={loading} />
      <MessageInput onSendMessage={sendMessage} disabled={loading} />
    </Box>
  );
};
