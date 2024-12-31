import React, { useState, useEffect, useRef } from 'react';
import { API_BASE_URL } from "../config";
import Wizard from './mealWizard';
import '../styles/chatroom.css';

function ChatRoom({ notifySuccess, notifyError }) {
    const [isWizardOpen, setIsWizardOpen] = useState(false);
    const messagesEndRef = useRef(null);
    const [room, setRoom] = useState('');
    const [messages, setMessages] = useState([]);
    const [message, setMessage] = useState('');
    const [recentChats, setRecentChats] = useState([]);
    const [userData, setUserData] = useState(null);
    const [contextMenuVisible, setContextMenuVisible] = useState(false);
    const [contextMenuPosition, setContextMenuPosition] = useState({ x: 0, y: 0 });
    const [selectedChatId, setSelectedChatId] = useState(null);
    const wsRef = useRef(null);
    const [isEditingTitle, setIsEditingTitle] = useState(false); // New state for editing title
    const [editedTitle, setEditedTitle] = useState('');

    const isMessageUnique = (messages, newMessage) => {
        return !messages.some((message) => message.id === newMessage.id);
    };
    const handleChatClick = async (chatId, displayName) => {
        setSelectedChatId(chatId); // Ensure chatId is set
        setRoom(displayName || chatId);
        setMessages([]); // Clear current messages
        await fetchMessages(chatId); // Fetch all existing messages
        connectToWebSocket(chatId); // Open WebSocket after fetching messages
    };

    const formatTimestamp = (timestamp) => {
        const now = new Date();
        const chatDate = new Date(timestamp);
        if (
            now.getFullYear() === chatDate.getFullYear() &&
            now.getMonth() === chatDate.getMonth() &&
            now.getDate() === chatDate.getDate()
        ) {
            return format(chatDate, 'HH:mm'); // Format time for today's chats
        } else {
            return format(chatDate, 'dd-MM-yy'); // Format date for other days
        }
    };

    const handleContextMenu = (e, chatId) => {
        e.preventDefault();
        setContextMenuPosition({ x: e.clientX, y: e.clientY });
        setSelectedChatId(chatId);
        setContextMenuVisible(true);
    };

    const handleDeleteChat = async () => {
        try {
            const token = localStorage.getItem("token");
            const res = await fetch(`${API_BASE_URL}/chat/delete/${selectedChatId}`, {
                method: "DELETE",
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
            if (res.ok) {
                // Remove the chat from the recent chats list
                setRecentChats(recentChats.filter((chat) => chat.id !== selectedChatId));
                setRoom('');  // Clear current room
                setMessages([]);  // Clear current messages
                console.log("Chat deleted successfully");
            } else {
                notifyError("Failed to delete chat.");
            }
        } catch (err) {
            notifyError("An error occurred while deleting the chat.");
        }
    };

    const closeContextMenu = () => {
        setContextMenuVisible(false);
    };

    const scrollToBottom = () => {
        if (messagesEndRef.current) {
            messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    };
    useEffect(() => {
        scrollToBottom();
    }, [messages]);
    useEffect(() => {
        fetchRecentChats();
        fetchUser();
    }, []);

    const syncMessages = async (chatId, lastTimestamp) => {
        const token = localStorage.getItem("token");
        try {
            const res = await fetch(
                `${API_BASE_URL}/chat/${chatId}/sync-messages?since=${encodeURIComponent(lastTimestamp)}`,
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }
            );
            if (res.ok) {
                const newMessages = await res.json();
                setMessages((prevMessages) => [
                    ...prevMessages,
                    ...newMessages.filter((msg) => isMessageUnique(prevMessages, msg)),
                ]);
            } else {
                console.error("Failed to sync messages");
                notifyError("Could not sync messages.");
            }
        } catch (err) {
            console.error("Error syncing messages:", err);
            notifyError("An error occurred while syncing messages.");
        }
    };

    const connectToWebSocket = async (chatId) => {
        const token = localStorage.getItem("token");

        // Initialize WebSocket connection first
        if (wsRef.current) {
            wsRef.current.close();
        }
        wsRef.current = new WebSocket(`${API_BASE_URL}/chat/room?chatid=${chatId}&token=${token}`);
        wsRef.current.onopen = () => {
            console.log(`Connected to chat room: ${chatId}`);
        };
        wsRef.current.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log("Received WebSocket Message:", data); // Debug incoming message

                const { id, timestamp, sender, content , type} = data;
                setMessages((prev) => [
                    ...prev,
                    { id, timestamp, user_id: sender, message: content, type: type},
                ]);
            } catch (err) {
                console.error("Error parsing WebSocket message:", err);
            }
        };
        wsRef.current.onclose = () => {
            console.log(`Disconnected from chat room: ${chatId}`);
        };
        wsRef.current.onerror = (error) => {
            console.error("WebSocket error:", error);
            notifyError("WebSocket connection error.");
        };

        // Sync messages after WebSocket is open
        const lastTimestamp = messages.length ? messages[messages.length - 1].timestamp : null;
        if (lastTimestamp) {
            try {
                await syncMessages(chatId, lastTimestamp);
            } catch (err) {
                console.error("Error syncing messages:", err);
            }
        }
    };



    const fetchUser = async () => {
        try {
            const token = localStorage.getItem("token");
            const res = await fetch(`${API_BASE_URL}/management/account`, {
                headers: { Authorization: `Bearer ${token}` },
            });
            if (res.ok) {
                const backendData = await res.json();
                setUserData(backendData);
                notifySuccess("User data fetched successfully.");
            } else {
                notifyError("Failed to fetch user information.");
            }
        } catch (err) {
            notifyError("An error occurred while fetching user data.");
        }
    };

    const fetchRecentChats = async () => {
        try {
            const token = localStorage.getItem("token");
            const res = await fetch(`${API_BASE_URL}/chat/chats`, {
                headers: { Authorization: `Bearer ${token}` },
            });
            if (res.ok) {
                const chats = await res.json();
                console.log(chats)
                setRecentChats(chats);
            } else {
                notifyError("Failed to fetch recent chats.");
            }
        } catch (err) {
            notifyError("An error occurred while fetching recent chats.");
        }
    };

    const fetchMessages = async (chatId) => {
        const token = localStorage.getItem("token");
        try {
            const res = await fetch(`${API_BASE_URL}/chat/${chatId}/messages`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
            if (res.ok) {
                const messagesData = await res.json();
                console.log(messagesData)
                setMessages(messagesData);
            } else {
                console.error("Failed to fetch messages");
                notifyError("Could not load messages.");
            }
        } catch (err) {
            console.error("Error fetching messages:", err);
            notifyError("An error occurred while fetching messages.");
        }
    };
    const startNewChat = () => {
        setIsWizardOpen(true);
    };

    const handleWizardComplete = (wizardData) => {
        setIsWizardOpen(false);
        // Use wizardData to customize the new chat
        // Example: Send wizardData to the server or log it
        console.log("Wizard completed with data:", wizardData);
        // Start the chat
        startNewChatLogic(wizardData);
    };

    const startNewChatLogic = async (wizardData) => {
        try {
            const token = localStorage.getItem("token");
            const parse = await fetch(`${API_BASE_URL}/management/account`, {
                method: "GET",
                headers: {
                    Authorization: `Bearer ${token}`,
                    "Content-Type": "application/json",
                }
            });
            const user = await parse.json(); // Parse the response body as JSON
            const data = {
                ...wizardData,
                ...user,
            };
            const displayName = wizardData.cravingfor;
            const res = await fetch(`${API_BASE_URL}/chat/new?display_name=${displayName}`, {
                method: "POST",
                headers: {
                    Authorization: `Bearer ${token}`,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(data), // Include the data in the body
            });

            if (res.ok) {
                const chat = await res.json();
                setRoom(chat.display_name || chat.id);
                setMessages([]);
                setRecentChats((prevChats) => [ chat, ...prevChats]);
                connectToWebSocket(chat.id);
                notifySuccess("New chat started!");
            } else {
                notifyError("Failed to start a new chat.");
            }
        } catch (err) {
            notifyError("An error occurred while starting a new chat.");
        }
    };


    const sendMessage = () => {
        if (!message.trim()) return;

        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(message);

            // Add the sent message with the correct structure to the messages state
            const timestamp = new Date().toISOString();
            setMessages((prev) => [
                ...prev,
                {
                    id: `temp-${Date.now()}`, // Temporary ID until a backend response provides the real ID
                    timestamp,
                    user_id: "You", // Represent the current user
                    message: message, // Use `message` to align with the rendering logic
                    type: "sent", // Explicitly mark as "sent"
                },
            ]);

            setMessage('');
        }
    };

const handleTitleSave = async () => {
    if (!selectedChatId) {
        notifyError("No chat selected.");
        return;
    }

    if (editedTitle.trim() === "") {
        notifyError("Title cannot be empty.");
        return;
    }

    try {
        const token = localStorage.getItem("token");
        const res = await fetch(`${API_BASE_URL}/chat/${selectedChatId}/metadata`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({ display_name: editedTitle }),
        });

        if (res.ok) {
            setRoom(editedTitle); // Update the displayed room name
            setRecentChats((prevChats) =>
                prevChats.map((chat) =>
                    chat.id === selectedChatId
                        ? { ...chat, display_name: editedTitle }
                        : chat
                )
            ); // Update the sidebar
            notifySuccess("Chat title updated successfully!");
            setIsEditingTitle(false);
        } else {
            notifyError("Failed to update chat title.");
        }
    } catch (err) {
        console.error("Error updating chat title:", err);
        notifyError("An error occurred while updating the chat title.");
    }
};



    return (
    <div className="chat-container">
        {isWizardOpen ? (
            <Wizard onComplete={handleWizardComplete} />
        ) : (
            <>
                <div className="sidebar">
                    <button className="button" onClick={startNewChat}>
                        New Chat
                    </button>
                    <h3>Recent Chats</h3>
                    <ul className="chat-list">
                        {recentChats.map((chat) => (
                            <li
                                key={chat.id}
                                onClick={() => handleChatClick(chat.id, chat.display_name || chat.id)}
                                onContextMenu={(e) => handleContextMenu(e, chat.id)} // Context menu event
                            >
                                <span>{chat.display_name || chat.id}</span>
                                <span className="timestamp">
                                    {/* {chat.last_activity ? formatTimestamp(chat.last_activity) : 'No activity'} */}
                                </span>
                            </li>
                        ))}
                    </ul>
                </div>
                <main className="chat-main">
                    <div
                        className="chat-title-container"
                        onMouseEnter={() => setIsEditingTitle(true)}
                        onMouseLeave={() => setIsEditingTitle(false)}
                    >
                        {isEditingTitle ? (
                            <div className="edit-title">
                                <input
                                    type="text"
                                    value={editedTitle || room}
                                    onChange={(e) => setEditedTitle(e.target.value)}
                                    onKeyDown={(e) => e.key === "Enter" && handleTitleSave()}
                                />
                                <button className="send-button" onClick={handleTitleSave}>Save</button>
                            </div>
                        ) : (
                            <h2 className="chat-title">{room || "Unknown Room"}</h2>
                        )}
                    </div>

                    <div className="messages">
                        {messages.map((m, index) => (
                            <div
                                key={m.id || index}
                                className={`message ${m.type === "received" ? "received" : "sent"}`}
                            >
                                {m.type === "received" ? (
                                    <span>
                                        <strong>{m.user_id}:</strong> {m.message}
                                    </span>
                                ) : (
                                    <span>{m.message}</span>
                                )}
                            </div>
                        ))}
                        <div ref={messagesEndRef} />
                    </div>

                    <div className="input-area">
                        <input
                            placeholder="Type message..."
                            value={message}
                            onChange={(e) => setMessage(e.target.value)}
                            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                        />
                        <button onClick={sendMessage}>Send</button>
                    </div>
                </main>
                {/* Context Menu */}
                {contextMenuVisible && (
                    <div
                        className="context-menu"
                        style={{
                            position: "absolute",
                            top: contextMenuPosition.y,
                            left: contextMenuPosition.x,
                        }}
                        onClick={closeContextMenu}
                    >
                        <button onClick={handleDeleteChat}>Delete Chat</button>
                    </div>
                )}
            </>
        )}
    </div>
);

}

export default ChatRoom;
