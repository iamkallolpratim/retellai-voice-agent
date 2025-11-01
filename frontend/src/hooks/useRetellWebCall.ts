import { useState, useCallback, useEffect, useRef } from 'react';
import { RetellWebClientService } from '../services/retellWebClient';

export interface TranscriptItem {
  role: 'agent' | 'user';
  content: string;
  timestamp: number;
}

export interface CallState {
  isActive: boolean;
  isAgentTalking: boolean;
  transcript: TranscriptItem[];
  error: string | null;
}

export function useRetellWebCall() {
  const [callState, setCallState] = useState<CallState>({
    isActive: false,
    isAgentTalking: false,
    transcript: [],
    error: null,
  });

  const clientRef = useRef<RetellWebClientService | null>(null);

  // Initialize client
  useEffect(() => {
    clientRef.current = new RetellWebClientService();

    return () => {
      if (clientRef.current) {
        clientRef.current.destroy();
      }
    };
  }, []);

  const startCall = useCallback(async (accessToken: string, sampleRate?: number) => {
    if (!clientRef.current) {
      throw new Error('Retell client not initialized');
    }

    // Setup event listeners
    clientRef.current.setupEventListeners({
      onCallStarted: () => {
        setCallState(prev => ({
          ...prev,
          isActive: true,
          error: null,
          transcript: [],
        }));
      },
      onCallEnded: () => {
        setCallState(prev => ({
          ...prev,
          isActive: false,
          isAgentTalking: false,
        }));
      },
      onAgentStartTalking: () => {
        setCallState(prev => ({ ...prev, isAgentTalking: true }));
      },
      onAgentStopTalking: () => {
        setCallState(prev => ({ ...prev, isAgentTalking: false }));
      },
      onUpdate: (update) => {
        // Handle transcript updates
        if (update.transcript) {
          const newTranscript: TranscriptItem[] = update.transcript.map((item: any) => ({
            role: item.role,
            content: item.content,
            timestamp: Date.now(),
          }));
          setCallState(prev => ({ ...prev, transcript: newTranscript }));
        }
      },
      onError: (error) => {
        setCallState(prev => ({
          ...prev,
          error: error.message,
          isActive: false,
          isAgentTalking: false,
        }));
      },
    });

    try {
      await clientRef.current.startCall(accessToken, sampleRate);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to start call';
      setCallState(prev => ({ ...prev, error: message }));
      throw error;
    }
  }, []);

  const stopCall = useCallback(async () => {
    if (!clientRef.current) return;

    try {
      await clientRef.current.stopCall();
    } catch (error) {
      console.error('Failed to stop call:', error);
    }
  }, []);

  return {
    callState,
    startCall,
    stopCall,
  };
}