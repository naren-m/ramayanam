import { ChatMessage, Conversation, ConversationSummary, AIStatus, AIProvider } from '../types';

const API_BASE = '/api/chat';

export class ChatService {
  private static instance: ChatService;

  static getInstance(): ChatService {
    if (!ChatService.instance) {
      ChatService.instance = new ChatService();
    }
    return ChatService.instance;
  }

  async createConversation(conversationId?: string): Promise<{ conversation_id: string }> {
    const response = await fetch(`${API_BASE}/conversations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        conversation_id: conversationId,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to create conversation');
    }

    return response.json();
  }

  async getConversation(conversationId: string): Promise<Conversation> {
    const response = await fetch(`${API_BASE}/conversations/${conversationId}`);

    if (!response.ok) {
      throw new Error('Failed to get conversation');
    }

    return response.json();
  }

  async sendMessage(
    conversationId: string,
    message: string,
    textId?: string
  ): Promise<{ conversation_id: string; response: ChatMessage }> {
    const response = await fetch(`${API_BASE}/conversations/${conversationId}/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        text_id: textId,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to send message');
    }

    return response.json();
  }

  async getConversationSummary(conversationId: string): Promise<ConversationSummary> {
    const response = await fetch(`${API_BASE}/conversations/${conversationId}/summary`);

    if (!response.ok) {
      throw new Error('Failed to get conversation summary');
    }

    return response.json();
  }

  async getAIStatus(): Promise<AIStatus> {
    const response = await fetch(`${API_BASE}/ai/status`);

    if (!response.ok) {
      throw new Error('Failed to get AI status');
    }

    return response.json();
  }

  async getAvailableProviders(): Promise<{ providers: AIProvider[]; current: string }> {
    const response = await fetch(`${API_BASE}/ai/providers`);

    if (!response.ok) {
      throw new Error('Failed to get available providers');
    }

    return response.json();
  }

  async getSuggestions(textId?: string, topic?: string): Promise<{ suggestions: string[] }> {
    const response = await fetch(`${API_BASE}/suggestions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text_id: textId,
        topic: topic,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to get suggestions');
    }

    return response.json();
  }
}

export const chatService = ChatService.getInstance();