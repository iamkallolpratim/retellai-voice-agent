import { AgentConfigCreate, AgentConfig, CallRequest, Call, CallResult } from "../types";

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

class APIService {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const config: RequestInit = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error);
      throw error;
    }
  }

  // Agent Configuration APIs
  async createAgentConfig(data: AgentConfigCreate): Promise<AgentConfig> {
    return this.request<AgentConfig>('/agents', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async listAgentConfigs(): Promise<AgentConfig[]> {
    return this.request<AgentConfig[]>('/agents');
  }

  async getAgentConfig(id: string): Promise<AgentConfig> {
    return this.request<AgentConfig>(`/agents/${id}`);
  }

  async updateAgentConfig(id: string, data: Partial<AgentConfigCreate>): Promise<AgentConfig> {
    return this.request<AgentConfig>(`/agents/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deleteAgentConfig(id: string): Promise<{ success: boolean; message: string }> {
    return this.request(`/agents/${id}`, { method: 'DELETE' });
  }

  // Call APIs
  async createCall(data: CallRequest): Promise<Call> {
    return this.request<Call>('/calls', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async listCalls(limit: number = 50, offset: number = 0): Promise<Call[]> {
    return this.request<Call[]>(`/calls?limit=${limit}&offset=${offset}`);
  }

  async getCall(id: string): Promise<Call> {
    return this.request<Call>(`/calls/${id}`);
  }

  async getCallStatus(id: string): Promise<Call> {
    return this.request<Call>(`/calls/${id}/status`);
  }

  async getCallResult(id: string): Promise<CallResult> {
    return this.request<CallResult>(`/calls/${id}/result`);
  }
}

export const apiService = new APIService(API_BASE_URL);