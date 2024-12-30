import React, { useState, useEffect, useRef } from 'react';
import { API_BASE_URL } from "../config";
import '../styles/chatroom.css';

function ChatRoom({ notifySuccess, notifyError }) {
  const messagesEndRef = useRef(null);
  const [room, setRoom] = useState(null);
  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState('');
  const [chats, setChats] = useState([]); // List of recent chats
  const wsRef = useRef(null); // WebSocket ref
  const [showChat, setShowChat] = useState(false);

  useEffect(() => {
    fetchChats(); // Fetch recent chats on component load
  }, []);

  // Fetch recent chats
  const fetchChats = async () => {
    try {
      const token = localStorage.getItem("token");
      const userId = localStorage.getItem("user_id"); // Ensure user_id is stored in localStorage
      const res = await fetch(`${API_BASE_URL}/user/${userId}/chats`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (res.ok) {
        const data = await res.json();
        setChats(data);
        notifySuccess("Chats fetched successfully.");
      } else {
        notifyError("Failed to fetch chats.");
      }
    } catch (err) {
      notifyError("An error occurred while fetching chats.");
    }
  };

  // Handle new chat creation
  const createNewChat = async () => {
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`${API_BASE_URL}/chats/new`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ participants: [] }), // Add participants as needed
      });

      if (res.ok) {
        const newChat = await res.json();
        setChats((prev) => [newChat, ...prev]); // Add new chat to the top of the list
        setRoom(newChat.id); // Set the new chat as the current room
        setShowChat(true);
        notifySuccess("New chat created successfully.");
      } else {
        notifyError("Failed to create a new chat.");
      }
    } catch (err) {
      notifyError("An error occurred while creating a new chat.");
    }
  };

  // Handle chat selection
  const selectChat = (chatId) => {
    setRoom(chatId);
    setShowChat(true);
  };

  const sendMessage = () => {
    if (!message.trim()) return;
    const newMessages = [...messages, `You: ${message}`];
    setMessages(newMessages);
    setMessage('');
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="chat-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <button className="button" onClick={createNewChat}>
          New Chat
        </button>
        <div className="recent-chats">
          <h3>Recent Chats</h3>
          {chats.map((chat) => (
            <div
              key={chat.id}
              className="chat-item"
              onClick={() => selectChat(chat.id)}
            >
              {chat.display_name || "Unnamed Chat"}
            </div>
          ))}
        </div>
      </aside>

      {/* Chat Main */}
      {showChat ? (
        <main className="chat-main">
          <h2 className="chat-title">Chat Room ({room})</h2>
          <div className="messages">
            {messages.map((m, index) => (
              <div key={index} className={`message ${m.startsWith("You:") ? "sent" : "received"}`}>
                {m}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
          <div className="input-area">
            <input
              className="input-field"
              placeholder="Type message..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            />
            <button className="send-button" onClick={sendMessage}>
              Send
            </button>
          </div>
        </main>
      ) : (
        <div className="welcome-message">Select or create a chat to get started!</div>
      )}
    </div>
  );
}

export default ChatRoom;
