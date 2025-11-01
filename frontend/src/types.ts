export interface AgentConfig {
    id: string;
    name: string;
    system_prompt: string;
    backchanneling: boolean;
    filler_words: boolean;
    interruption_sensitivity: number;
    scenario_type: 'check-in' | 'emergency';
    retell_agent_id?: string;
    created_at?: string;
    updated_at?: string;
  }
  
  export interface AgentConfigCreate {
    name: string;
    system_prompt: string;
    backchanneling: boolean;
    filler_words: boolean;
    interruption_sensitivity: number;
    scenario_type: 'check-in' | 'emergency';
  }
  
  export interface CallRequest {
    agent_config_id: string;
    driver_name: string;
    phone_number: string;
    load_number: string;
  }
  
  export interface Call {
    id: string;
    agent_config_id: string;
    driver_name: string;
    phone_number: string;
    load_number: string;
    retell_call_id?: string;
    status: 'pending' | 'in_progress' | 'completed' | 'failed';
    created_at: string;
    completed_at?: string;
    access_token?: string;
    sample_rate?: number;
  }
  
  export interface CallResult {
    id: string;
    call_id: string;
    structured_data: Record<string, any>;
    transcript: string;
    call_duration?: number;
    created_at: string;
  }
  
  export interface Notification {
    type: 'success' | 'error' | 'info';
    message: string;
  }

  export interface AppNotification {
    type: 'success' | 'error' | 'info';
    message: string;
  }
  
  export type TabType = 'config' | 'call' | 'results';