# MemoGenius Client 🧠✨

## Overview

MemoGenius Client is a modern web application that serves as a personal assistant to help you manage reminders and chat with an AI assistant. This React-based frontend interfaces with a Python backend server to provide a seamless experience for organizing your life.

## Features 🚀

- **Smart Chat**: Interact with an AI assistant through a clean chat interface
- **Reminder Management**: Create, edit, and delete reminders with due dates
- **Dashboard**: Quick overview of your recent reminders and fast access to chat
- **Responsive Design**: Works on both desktop and mobile devices

## Technologies Used 💻

- React 19
- TypeScript
- Material UI 6
- Vite
- Axios for API calls
- React Router for navigation

## Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Backend server running (see [Backend Repository](../backend/))

## Installation 🔧

1. Clone the repository:
   ```bash
   git clone https://github.com/andrea9293/memogenius.git
   cd memogenius/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file if needed (configure any environment variables)

## Running the Application 🚀

To start the development server:

```bash
npm run dev
```

The application will be available at `http://localhost:5173` by default.

## Building for Production

To create a production build:

```bash
npm run build
```

The built files will be in the `dist` directory.

## Backend Repository

This client interfaces with a Python backend server. You can find the backend repository at: [Link to be provided]

## Authentication 🔐

The application uses a token-based authentication system. Users need to:

1. Get an access key from the MemoGenius Telegram bot
2. Enter this key in the web application login screen

## Project Structure

- `frontend/`
  - `/components` - UI components organized by feature
  - `/context` - React context providers for state management
  - `/hooks` - Custom React hooks
  - `/pages` - Main application pages
  - `/services` - API service connections
  - `/types` - TypeScript type definitions

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the [GNU Affero General Public License v3.0](LICENSE) - see the LICENSE file for details.

Copyright (c) 2024
