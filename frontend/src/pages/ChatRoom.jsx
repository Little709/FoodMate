import React, { useState, useEffect, useRef } from 'react';
import { API_BASE_URL } from "../config";
import Wizard from './mealWizard'; // Import your Wizard component
import '../styles/chatroom.css';

function ChatRoom({ notifySuccess, notifyError }) {
    const messagesEndRef = useRef(null);
  const [room, setRoom] = useState('couple-room-123');
  const [messages, setMessages] = useState(
    JSON.parse(localStorage.getItem('chat_messages')) || []
  );
  const [message, setMessage] = useState('');
  const wsRef = useRef(null); // WebSocket ref
  const [userData, setUserData] = useState(null);
  const [resumeChat, setResumeChat] = useState(
    JSON.parse(localStorage.getItem('resume_chat')) || false
  );

  // Scroll to the bottom of the messages
  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };
  const [showChat, setShowChat] = useState(false);
    useEffect(() => {
      fetchUser();
    }, []);
  // Save messages and resume state to localStorage
  useEffect(() => {
    localStorage.setItem('chat_messages', JSON.stringify(messages));
    localStorage.setItem('resume_chat', JSON.stringify(resumeChat));
  }, [messages, resumeChat]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Establish WebSocket connection
  useEffect(() => {
    if ((showChat || resumeChat) && !wsRef.current) {
      const token = localStorage.getItem("token");
      if (!token) {
        notifyError("User is not authenticated. Please log in.");
        return;
      }

      const socket = new WebSocket(`ws://localhost:8000/chat/ws/${room}?token=${token}`);
      wsRef.current = socket;

      console.log("Initializing WebSocket:", socket);

      socket.onopen = () => {
        console.log('Connected to chat server');
        notifySuccess('Connected to chat server.');
      };

      socket.onmessage = (e) => {
        console.log('Message received:', e.data);
        setMessages((prev) => {
          const updatedMessages = [...prev, e.data];
          localStorage.setItem('chat_messages', JSON.stringify(updatedMessages)); // Save to localStorage
          return updatedMessages;
        });

      };

      socket.onerror = (err) => {
        console.error("WebSocket error occurred:", err);
        notifyError("WebSocket connection failed.");

      };

      socket.onclose = (e) => {
        console.log('Disconnected from chat server:', e.reason || "No reason provided");
        notifySuccess('Disconnected from chat server.');
        wsRef.current = null; // Clean up ref
      };

      return () => {
        console.log("Cleaning up WebSocket connection...");
        socket.close();
      };
    }
  }, [showChat, resumeChat, room]);

    const sendMessage = (data = null) => {
      const messageToSend = data ? JSON.stringify(data) : message.trim();

      if (!messageToSend) return; // Exit if there's no message to send

      const interval = setInterval(() => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          wsRef.current.send(messageToSend);

          // Add message to chat if it's a user message (not Wizard data)
          if (!data) {
            const newMessage = `You: ${message.trim()}`;
            setMessages((prev) => {
              const updatedMessages = [...prev, newMessage];
              localStorage.setItem('chat_messages', JSON.stringify(updatedMessages));
              return updatedMessages;
            });
            setMessage(""); // Clear input field
          }

//           notifySuccess(data ? "Wizard data sent to chat server." : "Message sent successfully.");
          clearInterval(interval); // Stop retrying
//           scrollToBottom();
        }
      }, 500); // Retry every 500ms
    };
const fetchUser = async () => {
  try {
    const token = localStorage.getItem("token");
    const res = await fetch(`${API_BASE_URL}/management/account`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    if (res.ok) {
      const backendData = await res.json();
      const savedWizardData = JSON.parse(localStorage.getItem('userData')) || {};
      const combinedData = { ...backendData, ...savedWizardData };
      setUserData(combinedData);
      notifySuccess("User data fetched successfully.");
    } else {
      notifyError("Failed to fetch user information.");
    }
  } catch (err) {
    notifyError("An error occurred while fetching user data.");
  }
};
  const sendDataWhenReady = (data) => {
    const interval = setInterval(() => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify(data));
        notifySuccess("Wizard data sent to chat server.");
        clearInterval(interval);
      }
    }, 500); // Retry every 500ms
  };

const handleWizardComplete = (data) => {
  console.log('Wizard Data:', data);

  // If reuseMessages is false, clear chat zhistory
  if (data.reuseMessages == false) {
    console.log("new populating")
    localStorage.removeItem('chat_messages');
    const jointData = { ...userData, ...data };
    setUserData(jointData);
    sendDataWhenReady(jointData)
    setMessages([]);
    notifySuccess("Chat messages cleared.");
  } else {
    console.log("re-populating")
    // Retrieve messages from localStorage
    const storedMessages = JSON.parse(localStorage.getItem('chat_messages')) || [];
    console.log(storedMessages)
    setMessages(storedMessages);
    notifySuccess("Chat messages retrieved.");
  }

  // Handle the rest of the wizard data
  const jointData = { ...userData, ...data };
  setUserData(jointData);
  setShowChat(true);
  notifySuccess("Wizard completed successfully.");
};

  const handleResume = () => {
    setResumeChat(true);
    setShowChat(true);
    notifySuccess("Resuming chat...");
  };

  if (!showChat) {
    return <Wizard onComplete={handleWizardComplete} onResume={handleResume} />;
  }

  return (
    <div className="chat-container">
      <main className="chat-main">
        <h2 className="chat-title">Chat Room ({room})</h2>
        <div className="messages">
          {messages.map((m, index) => {
            const isSentByUser = m.startsWith("You:");
            return (
              <div
                key={index}
                className={`message ${isSentByUser ? "sent" : "received"}`}
              >
                {m}
              </div>
            );
          })}
          <div ref={messagesEndRef} /> {/* Invisible div for scrolling */}
        </div>
        <div className="input-area">
          <input
            className="input-field"
            placeholder="Type message..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
          />
          <button className="button send-button" onClick={sendMessage}>
            Send
          </button>
        </div>
        <h3>User Dietary Info</h3>
        <pre className="user-data">
          {userData ? JSON.stringify(userData, null, 2) : 'Loading user data...'}
        </pre>
      </main>
    </div>
  );
}

export default ChatRoom;
