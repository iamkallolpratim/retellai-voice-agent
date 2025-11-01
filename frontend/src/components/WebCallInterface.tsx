import React, { useState, useEffect } from 'react';
import { Phone, PhoneOff, Mic, MicOff, Volume2, AlertCircle } from 'lucide-react';
import { useRetellWebCall } from '../hooks/useRetellWebCall';

interface WebCallInterfaceProps {
  accessToken: string;
  sampleRate?: number;
  driverName: string;
  loadNumber: string;
  onCallEnd: () => void;
}

export const WebCallInterface: React.FC<WebCallInterfaceProps> = ({
  accessToken,
  sampleRate,
  driverName,
  loadNumber,
  onCallEnd,
}) => {
  const { callState, startCall, stopCall } = useRetellWebCall();
  const [isMuted, setIsMuted] = useState(false);
  const [callDuration, setCallDuration] = useState(0);
  const [isInitializing, setIsInitializing] = useState(true);
  const [initError, setInitError] = useState<string | null>(null);

  // Start call on mount
  useEffect(() => {
    let mounted = true;

    const initializeCall = async () => {
      if (!accessToken) {
        setInitError('No access token provided');
        setIsInitializing(false);
        return;
      }

      console.log('🎯 Initializing web call...');
      
      try {
        // Small delay to ensure component is fully mounted
        await new Promise(resolve => setTimeout(resolve, 500));
        
        if (mounted) {
          await startCall(accessToken, sampleRate);
          setIsInitializing(false);
          console.log('✅ Call initialized successfully');
        }
      } catch (error) {
        console.error('❌ Failed to initialize call:', error);
        if (mounted) {
          setInitError(error instanceof Error ? error.message : 'Failed to start call');
          setIsInitializing(false);
        }
      }
    };

    initializeCall();

    return () => {
      mounted = false;
      console.log('🧹 Cleaning up web call...');
      stopCall().catch(console.error);
    };
  }, [accessToken, sampleRate]);

  // Track call duration
  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (callState.isActive) {
      interval = setInterval(() => {
        setCallDuration((prev) => prev + 1);
      }, 1000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [callState.isActive]);

  const handleEndCall = async () => {
    console.log('🛑 Ending call...');
    await stopCall();
    onCallEnd();
  };

  const handleRetry = async () => {
    setInitError(null);
    setIsInitializing(true);
    
    try {
      await startCall(accessToken, sampleRate);
      setIsInitializing(false);
    } catch (error) {
      setInitError(error instanceof Error ? error.message : 'Failed to start call');
      setIsInitializing(false);
    }
  };

  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white border-4 border-black p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="border-b-2 border-black pb-4 mb-4">
          <h2 className="text-2xl font-bold">Live Web Call</h2>
          <div className="mt-2 space-y-1">
            <p className="text-sm">
              <span className="font-semibold">Driver:</span> {driverName}
            </p>
            <p className="text-sm">
              <span className="font-semibold">Load:</span> {loadNumber}
            </p>
          </div>
        </div>

        {/* Initialization State */}
        {isInitializing && (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <div className="w-16 h-16 border-4 border-black border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
              <p className="font-semibold text-lg">Connecting to agent...</p>
              <p className="text-sm text-gray-600 mt-2">
                Please allow microphone access when prompted
              </p>
            </div>
          </div>
        )}

        {/* Error State */}
        {initError && !isInitializing && (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center max-w-md">
              <AlertCircle className="w-16 h-16 text-red-600 mx-auto mb-4" />
              <p className="font-semibold text-lg text-red-600 mb-2">Connection Failed</p>
              <p className="text-sm text-gray-600 mb-4">{initError}</p>
              <div className="flex gap-3">
                <button
                  onClick={handleRetry}
                  className="flex-1 bg-black text-white py-3 px-6 font-bold hover:bg-gray-800 transition-colors"
                >
                  Retry Connection
                </button>
                <button
                  onClick={onCallEnd}
                  className="flex-1 border-2 border-black py-3 px-6 font-bold hover:bg-gray-100 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Active Call State */}
        {!isInitializing && !initError && (
          <>
            {/* Call Status */}
            <div className="mb-4">
              <div className="flex items-center justify-between p-4 border-2 border-black bg-gray-50">
                <div className="flex items-center gap-3">
                  {callState.isActive ? (
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                      <span className="font-semibold">Connected</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-gray-400 rounded-full"></div>
                      <span className="font-semibold">Connecting...</span>
                    </div>
                  )}
                </div>
                <div className="text-lg font-mono font-bold">{formatDuration(callDuration)}</div>
              </div>

              {callState.isAgentTalking && (
                <div className="mt-2 p-3 border-2 border-blue-600 bg-blue-50 flex items-center gap-2">
                  <Volume2 className="w-5 h-5 text-blue-600 animate-pulse" />
                  <span className="font-semibold text-blue-600">Agent is speaking...</span>
                </div>
              )}

              {callState.error && (
                <div className="mt-2 p-3 border-2 border-red-600 bg-red-50">
                  <span className="font-semibold text-red-600">Error: {callState.error}</span>
                </div>
              )}
            </div>

            {/* Transcript */}
            <div className="flex-1 overflow-y-auto border-2 border-black p-4 mb-4 bg-gray-50 min-h-[300px]">
              <h3 className="font-bold mb-3 text-sm uppercase tracking-wide">Live Transcript</h3>
              <div className="space-y-3">
                {callState.transcript.length === 0 ? (
                  <div className="text-center py-8">
                    <p className="text-gray-500 text-sm italic">
                      {callState.isActive 
                        ? "Conversation will appear here..."
                        : "Waiting for connection..."}
                    </p>
                  </div>
                ) : (
                  callState.transcript.map((item, index) => (
                    <div
                      key={index}
                      className={`p-3 border ${
                        item.role === 'agent'
                          ? 'border-blue-600 bg-blue-50'
                          : 'border-green-600 bg-green-50'
                      }`}
                    >
                      <div className="font-semibold text-xs uppercase mb-1">
                        {item.role === 'agent' ? '🤖 Agent' : '👤 Driver'}
                      </div>
                      <div className="text-sm">{item.content}</div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Controls */}
            <div className="flex gap-3">
              <button
                onClick={() => setIsMuted(!isMuted)}
                disabled={!callState.isActive}
                className={`flex-1 py-3 px-4 border-2 border-black font-bold transition-colors flex items-center justify-center gap-2 ${
                  isMuted
                    ? 'bg-red-100 text-red-600'
                    : 'bg-white hover:bg-gray-100'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                {isMuted ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                {isMuted ? 'Unmute' : 'Mute'}
              </button>

              <button
                onClick={handleEndCall}
                className="flex-1 bg-red-600 text-white py-3 px-4 border-2 border-black font-bold hover:bg-red-700 transition-colors flex items-center justify-center gap-2"
              >
                <PhoneOff className="w-5 h-5" />
                End Call
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};