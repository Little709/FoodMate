// frontend/src/pages/ChatRoom.jsx
import React, { useState, useEffect } from 'react';

function ChatRoom() {
  const [room, setRoom] = useState('couple-room-123');
  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState('');
  const [ws, setWs] = useState(null);

  useEffect(() => {
    const socket = new WebSocket(`ws://localhost:8000/chat/ws/${room}`);
    socket.onopen = () => console.log('Connected to chat server');
    socket.onmessage = (e) => {
      setMessages(prev => [...prev, e.data]);
    };
    socket.onclose = () => console.log('Disconnected from chat server');
    setWs(socket);

    return () => socket.close();
  }, [room]);

  const sendMessage = () => {
    if (ws) {
      ws.send(message);
      setMessage('');
    }
  };

  return (
    <div>
      <h2>Chat Room ({room})</h2>
      <div>
        {messages.map((m, index) => (
          <div key={index}>{m}</div>
        ))}
      </div>
      <input
        placeholder="Type message..."
        value={message}
        onChange={e => setMessage(e.target.value)}
        onKeyDown={e => e.key === 'Enter' && sendMessage()}
      />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
}

export default ChatRoom;
