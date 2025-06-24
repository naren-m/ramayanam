import React, { useState, useEffect, useRef } from 'react';
import { Send, MessageCircle, Sparkles, Book, User, Bot } from 'lucide-react';
import { ChatMessage, TextReference } from '../../types';
import { chatService } from '../../services/chatService';

interface ChatInterfaceProps {
  conversationId?: string;
  activeText?: string;
  onConversationChange?: (conversationId: string) => void;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  conversationId: propConversationId,
  activeText,
  onConversationChange,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(propConversationId || null);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (propConversationId) {
      loadConversation(propConversationId);
    } else {
      initializeNewConversation();
    }
  }, [propConversationId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    loadSuggestions();
  }, [activeText]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const initializeNewConversation = async () => {
    try {
      const result = await chatService.createConversation();
      setConversationId(result.conversation_id);
      onConversationChange?.(result.conversation_id);
    } catch (error) {
      console.error('Failed to create conversation:', error);
    }
  };

  const loadConversation = async (id: string) => {
    try {
      const conversation = await chatService.getConversation(id);
      setMessages(conversation.messages);
      setConversationId(id);
    } catch (error) {
      console.error('Failed to load conversation:', error);
    }
  };

  const loadSuggestions = async () => {
    try {
      const result = await chatService.getSuggestions(activeText);
      setSuggestions(result.suggestions);
    } catch (error) {
      console.error('Failed to load suggestions:', error);
    }
  };

  const sendMessage = async (message: string) => {
    if (!message.trim() || !conversationId || isLoading) return;

    const userMessage: ChatMessage = {
      message_id: `temp-${Date.now()}`,
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const result = await chatService.sendMessage(conversationId, message, activeText);
      
      // Replace temporary user message and add AI response
      setMessages(prev => {
        const filtered = prev.filter(msg => msg.message_id !== userMessage.message_id);
        return [...filtered, userMessage, result.response];
      });
    } catch (error) {
      console.error('Failed to send message:', error);
      // Add error message
      const errorMessage: ChatMessage = {
        message_id: `error-${Date.now()}`,
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your message. Please try again.',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(inputMessage);
  };

  const handleSuggestionClick = (suggestion: string) => {
    sendMessage(suggestion);
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-900">
      {/* Header */}
      <div className="flex items-center gap-3 p-4 border-b dark:border-gray-700">
        <MessageCircle className="w-6 h-6 text-blue-600" />
        <div>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Sacred Text Discussion
          </h2>
          {activeText && (
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Discussing: {activeText.charAt(0).toUpperCase() + activeText.slice(1)}
            </p>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center py-8">
            <Sparkles className="w-12 h-12 text-blue-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              Welcome to Sacred Text Chat
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              Ask questions about ancient wisdom, explore philosophical concepts, 
              or discuss verses and their meanings.
            </p>
            
            {/* Suggestions */}
            {suggestions.length > 0 && (
              <div className="max-w-md mx-auto">
                <p className="text-sm text-gray-500 mb-2">Try these questions:</p>
                <div className="space-y-2">
                  {suggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => handleSuggestionClick(suggestion)}
                      className="block w-full text-left px-3 py-2 text-sm text-blue-600 bg-blue-50 
                               hover:bg-blue-100 rounded-lg transition-colors"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          messages.map((message) => (
            <div key={message.message_id} className="space-y-2">
              <MessageBubble message={message} />
            </div>
          ))
        )}
        
        {isLoading && (
          <div className="flex items-center gap-2 text-gray-500">
            <Bot className="w-5 h-5" />
            <div className="flex gap-1">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t dark:border-gray-700">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Ask about sacred texts, philosophy, or specific verses..."
            className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 
                     focus:ring-blue-500 dark:bg-gray-800 dark:border-gray-600 
                     dark:text-white dark:placeholder-gray-400"
            disabled={isLoading || !conversationId}
          />
          <button
            type="submit"
            disabled={!inputMessage.trim() || isLoading || !conversationId}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 
                     disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </form>
      </div>
    </div>
  );
};

interface MessageBubbleProps {
  message: ChatMessage;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex gap-3 max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        {/* Avatar */}
        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
          isUser 
            ? 'bg-blue-600 text-white' 
            : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300'
        }`}>
          {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
        </div>

        {/* Message content */}
        <div className={`rounded-lg px-4 py-2 ${
          isUser
            ? 'bg-blue-600 text-white'
            : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white'
        }`}>
          <div className="text-sm leading-relaxed">{message.content}</div>
          
          {/* References */}
          {message.references && message.references.length > 0 && (
            <div className="mt-3 space-y-2">
              <div className="text-xs font-medium opacity-80">Related verses:</div>
              {message.references.map((ref, index) => (
                <ReferenceCard key={index} reference={ref} />
              ))}
            </div>
          )}
          
          {/* Timestamp */}
          <div className={`text-xs mt-2 ${
            isUser ? 'text-blue-100' : 'text-gray-500 dark:text-gray-400'
          }`}>
            {formatTimestamp(message.timestamp)}
          </div>
        </div>
      </div>
    </div>
  );
};

interface ReferenceCardProps {
  reference: TextReference;
}

const ReferenceCard: React.FC<ReferenceCardProps> = ({ reference }) => {
  return (
    <div className="bg-white bg-opacity-10 rounded p-2 text-xs">
      <div className="flex items-center gap-1 mb-1">
        <Book className="w-3 h-3" />
        <span className="font-medium">
          {reference.text_id}: {reference.hierarchy_path}
        </span>
      </div>
      <div className="text-xs opacity-90">{reference.excerpt}</div>
    </div>
  );
};

const formatTimestamp = (timestamp: string) => {
  return new Date(timestamp).toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit' 
  });
};