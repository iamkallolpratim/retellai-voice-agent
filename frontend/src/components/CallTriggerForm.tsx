// src/components/CallTriggerForm.tsx
import { Clock, Phone } from "lucide-react";
import { CallRequest, AgentConfig, Call } from "../types";
import { WebCallInterface } from "./WebCallInterface";
import { useState } from "react";

export const CallTriggerForm: React.FC<{
  request: CallRequest;
  onChange: (request: CallRequest) => void;
  onSubmit: () => void;
  onWebCallSubmit: (request: CallRequest) => Promise<Call>; 
  configs: AgentConfig[];
  isLoading: boolean;
}> = ({ request, onChange, onSubmit, onWebCallSubmit, configs, isLoading }) => {
  const [showWebCall, setShowWebCall] = useState(false);
  const [webCallData, setWebCallData] = useState<{
    accessToken: string;
    sampleRate: number;
    driverName: string;
    loadNumber: string;
  } | null>(null);
  const [isWebCallLoading, setIsWebCallLoading] = useState(false);

  // This is where the web call handler goes
  const handleStartWebCall = async () => {
    if (
      !request.agent_config_id ||
      !request.driver_name ||
      !request.load_number
    ) {
      alert('Please fill in all call details');
      return;
    }

    setIsWebCallLoading(true);
    try {
      // API call creates web call and returns access_token
      const response = await onWebCallSubmit(request);
      
      // Check if access_token exists
      if (!response.access_token) {
        throw new Error('No access token received from server');
      }

      // Show web call interface with real data from API
      setWebCallData({
        accessToken: response.access_token,
        sampleRate: response.sample_rate || 24000,
        driverName: request.driver_name,
        loadNumber: request.load_number,
      });
      setShowWebCall(true);
      
    } catch (error) {
      console.error('Failed to start web call:', error);
      alert(`Failed to start web call: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsWebCallLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div>
        <label className="block font-semibold mb-2">
          Select Agent Configuration *
        </label>
        <select
          value={request.agent_config_id}
          onChange={(e) =>
            onChange({ ...request, agent_config_id: e.target.value })
          }
          className="w-full p-3 border-2 border-black focus:outline-none focus:ring-2 focus:ring-gray-400"
        >
          <option value="">-- Select a configuration --</option>
          {configs.map((config) => (
            <option key={config.id} value={config.id}>
              {config.name}
            </option>
          ))}
        </select>
        {configs.length === 0 && (
          <p className="text-sm text-gray-600 mt-1">
            No configurations available. Create one in the Configure Agent tab.
          </p>
        )}
      </div>

      <div>
        <label className="block font-semibold mb-2">Driver Name *</label>
        <input
          type="text"
          value={request.driver_name}
          onChange={(e) =>
            onChange({ ...request, driver_name: e.target.value })
          }
          className="w-full p-3 border-2 border-black focus:outline-none focus:ring-2 focus:ring-gray-400"
          placeholder="e.g., Mike Johnson"
        />
      </div>

      <div>
        <label className="block font-semibold mb-2">Phone Number *</label>
        <input
          type="tel"
          value={request.phone_number}
          onChange={(e) =>
            onChange({ ...request, phone_number: e.target.value })
          }
          className="w-full p-3 border-2 border-black focus:outline-none focus:ring-2 focus:ring-gray-400"
          placeholder="e.g., +1 (555) 123-4567"
        />
        <p className="text-sm text-gray-600 mt-1">
          For web calls (non-USA), this is for reference only
        </p>
      </div>

      <div>
        <label className="block font-semibold mb-2">Load Number *</label>
        <input
          type="text"
          value={request.load_number}
          onChange={(e) =>
            onChange({ ...request, load_number: e.target.value })
          }
          className="w-full p-3 border-2 border-black focus:outline-none focus:ring-2 focus:ring-gray-400"
          placeholder="e.g., 7891-B"
        />
      </div>

      {/* Web Call Button - Uses handleStartWebCall */}
      <button
        onClick={handleStartWebCall}
        disabled={isWebCallLoading || isLoading || configs.length === 0}
        className="w-full bg-white text-black py-4 px-6 font-bold border-2 border-black hover:bg-gray-100 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        {isWebCallLoading ? (
          <>
            <Clock className="w-5 h-5 animate-spin" />
            Connecting Web Call...
          </>
        ) : (
          <>
            <Phone className="w-5 h-5" />
            Start Web Call (Demo)
          </>
        )}
      </button>

      {/* Regular Phone Call Button */}
      <button
        onClick={onSubmit}
        disabled={isLoading || configs.length === 0}
        className="w-full bg-black text-white py-4 px-6 font-bold hover:bg-gray-800 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        {isLoading ? (
          <>
            <Clock className="w-5 h-5 animate-spin" />
            Initiating Call...
          </>
        ) : (
          <>
            <Phone className="w-5 h-5" />
            Start Test Call
          </>
        )}
      </button>

      {/* Web Call Interface Modal */}
      {showWebCall && webCallData && (
        <WebCallInterface
          accessToken={webCallData.accessToken}
          sampleRate={webCallData.sampleRate}
          driverName={webCallData.driverName}
          loadNumber={webCallData.loadNumber}
          onCallEnd={() => {
            setShowWebCall(false);
            setWebCallData(null);
            // Optionally refresh the calls list
          }}
        />
      )}
    </div>
  );
};