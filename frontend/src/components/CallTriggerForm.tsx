import { Clock, Phone } from "lucide-react";
import { CallRequest, AgentConfig } from "../types";

export const CallTriggerForm: React.FC<{
    request: CallRequest;
    onChange: (request: CallRequest) => void;
    onSubmit: () => void;
    configs: AgentConfig[];
    isLoading: boolean;
  }> = ({ request, onChange, onSubmit, configs, isLoading }) => {
    return (
      <div className="space-y-4">
        <div>
          <label className="block font-semibold mb-2">Select Agent Configuration *</label>
          <select
            value={request.agent_config_id}
            onChange={(e) => onChange({ ...request, agent_config_id: e.target.value })}
            className="w-full p-3 border-2 border-black focus:outline-none focus:ring-2 focus:ring-gray-400"
          >
            <option value="">-- Select a configuration --</option>
            {configs.map((config) => (
              <option key={config.id} value={config.id}>{config.name}</option>
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
            onChange={(e) => onChange({ ...request, driver_name: e.target.value })}
            className="w-full p-3 border-2 border-black focus:outline-none focus:ring-2 focus:ring-gray-400"
            placeholder="e.g., Mike Johnson"
          />
        </div>
  
        <div>
          <label className="block font-semibold mb-2">Phone Number *</label>
          <input
            type="tel"
            value={request.phone_number}
            onChange={(e) => onChange({ ...request, phone_number: e.target.value })}
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
            onChange={(e) => onChange({ ...request, load_number: e.target.value })}
            className="w-full p-3 border-2 border-black focus:outline-none focus:ring-2 focus:ring-gray-400"
            placeholder="e.g., 7891-B"
          />
        </div>
  
        <button
          onClick={onSubmit}
          disabled={isLoading || configs.length === 0}
          className="w-full bg-black text-white py-4 px-6 font-bold hover:bg-gray-800 transition-colors disabled:bg-gray-400 flex items-center justify-center gap-2"
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
      </div>
    );
  };