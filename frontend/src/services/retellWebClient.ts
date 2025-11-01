// src/services/retellWebClient.ts
import { RetellWebClient } from "retell-client-js-sdk";

export interface RetellCallEvents {
  onCallStarted: () => void;
  onCallEnded: () => void;
  onError: (error: Error) => void;
  onUpdate: (update: any) => void;
  onAgentStartTalking: () => void;
  onAgentStopTalking: () => void;
}

export class RetellWebClientService {
  private client: RetellWebClient | null = null;
  private isCallActive: boolean = false;

  constructor() {
    // Initialize the client
    this.client = new RetellWebClient();
  }

  setupEventListeners(events: Partial<RetellCallEvents>) {
    if (!this.client) return;

    // Call started
    this.client.on("call_started", () => {
      console.log("✅ Call started successfully");
      this.isCallActive = true;
      events.onCallStarted?.();
    });

    // Call ended
    this.client.on("call_ended", () => {
      console.log("📞 Call ended");
      this.isCallActive = false;
      events.onCallEnded?.();
    });

    // Agent start talking
    this.client.on("agent_start_talking", () => {
      console.log("🗣️ Agent started talking");
      events.onAgentStartTalking?.();
    });

    // Agent stop talking
    this.client.on("agent_stop_talking", () => {
      console.log("🤫 Agent stopped talking");
      events.onAgentStopTalking?.();
    });

    // Call updates (transcript updates)
    this.client.on("update", (update) => {
      console.log("📝 Call update:", update);
      events.onUpdate?.(update);
    });

    // Metadata updates
    this.client.on("metadata", (metadata) => {
      console.log("📊 Metadata:", metadata);
    });

    // Errors
    this.client.on("error", (error) => {
      console.error("❌ Retell error:", error);
      this.isCallActive = false;
      events.onError?.(error);
    });
  }

  async startCall(accessToken: string, sampleRate?: number): Promise<void> {
    if (!this.client) {
      throw new Error("Retell client not initialized");
    }

    if (this.isCallActive) {
      console.warn("A call is already in progress, stopping previous call...");
      await this.stopCall();
    }

    console.log("🚀 Starting call with access token:", accessToken.substring(0, 20) + "...");

    try {
      // Request microphone permissions first
      await navigator.mediaDevices.getUserMedia({ audio: true });
      console.log("🎤 Microphone access granted");

      // Start the call with proper configuration
      await this.client.startCall({
        accessToken,
        sampleRate: sampleRate || 24000,
        emitRawAudioSamples: false,
      });
      
      console.log("✅ Call started successfully");
    } catch (error: any) {
      console.error("❌ Failed to start call:", error);
      
      // Provide more specific error messages
      if (error.name === 'NotAllowedError') {
        throw new Error('Microphone permission denied. Please allow microphone access and try again.');
      } else if (error.name === 'NotFoundError') {
        throw new Error('No microphone found. Please connect a microphone and try again.');
      } else if (error.message?.includes('timeout')) {
        throw new Error('Connection timeout. Please check your internet connection and try again.');
      } else if (error.message?.includes('access_token')) {
        throw new Error('Invalid access token. Please try creating a new call.');
      }
      
      throw error;
    }
  }

  async stopCall(): Promise<void> {
    if (!this.client) return;
    
    try {
      if (this.isCallActive) {
        await this.client.stopCall();
        console.log("📞 Call stopped");
      }
      this.isCallActive = false;
    } catch (error) {
      console.error("❌ Failed to stop call:", error);
      this.isCallActive = false;
      throw error;
    }
  }

  getCallStatus(): boolean {
    return this.isCallActive;
  }

  destroy() {
    if (this.client && this.isCallActive) {
      this.stopCall().catch(console.error);
    }
    this.client = null;
  }
}