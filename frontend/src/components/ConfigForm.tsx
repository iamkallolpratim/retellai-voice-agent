import { AgentConfigCreate } from "../types";

export const ConfigForm: React.FC<{
    config: AgentConfigCreate;
    onChange: (config: AgentConfigCreate) => void;
    onSubmit: () => void;
    onCancel?: () => void;
    isEditing: boolean;
    isLoading: boolean;
  }> = ({ config, onChange, onSubmit, onCancel, isEditing, isLoading }) => {
    return (
      <div className="space-y-4">
        <div>
          <label className="block font-semibold mb-2">Configuration Name *</label>
          <input
            type="text"
            value={config.name}
            onChange={(e) => onChange({ ...config, name: e.target.value })}
            className="w-full p-3 border-2 border-black focus:outline-none focus:ring-2 focus:ring-gray-400"
            placeholder="e.g., Standard Check-in Agent"
          />
        </div>
  
        <div>
          <label className="block font-semibold mb-2">Scenario Type *</label>
          <select
            value={config.scenario_type}
            onChange={(e) => onChange({ ...config, scenario_type: e.target.value as 'check-in' | 'emergency' })}
            className="w-full p-3 border-2 border-black focus:outline-none focus:ring-2 focus:ring-gray-400"
          >
            <option value="check-in">End-to-End Driver Check-in</option>
            <option value="emergency">Dynamic Emergency Protocol</option>
          </select>
        </div>
  
        <div>
          <label className="block font-semibold mb-2">System Prompt *</label>
          <textarea
            value={config.system_prompt}
            onChange={(e) => onChange({ ...config, system_prompt: e.target.value })}
            className="w-full p-3 border-2 border-black h-40 focus:outline-none focus:ring-2 focus:ring-gray-400 font-mono text-sm"
            placeholder="Define the agent's behavior... Use {driver_name} and {load_number} as variables."
          />
          <p className="text-sm text-gray-600 mt-1">
            Tip: Use {'{driver_name}'} and {'{load_number}'} as variables
          </p>
        </div>
  
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-center justify-between p-4 border-2 border-black">
            <div>
              <span className="font-semibold block">Backchanneling</span>
              <span className="text-xs text-gray-600">Natural acknowledgments</span>
            </div>
            <button
              type="button"
              onClick={() => onChange({ ...config, backchanneling: !config.backchanneling })}
              className={`w-12 h-6 rounded-full transition-colors ${config.backchanneling ? 'bg-black' : 'bg-gray-300'}`}
            >
              <div className={`w-5 h-5 rounded-full bg-white transition-transform ${config.backchanneling ? 'translate-x-6' : 'translate-x-1'}`} />
            </button>
          </div>
  
          <div className="flex items-center justify-between p-4 border-2 border-black">
            <div>
              <span className="font-semibold block">Filler Words</span>
              <span className="text-xs text-gray-600">Um, uh, you know</span>
            </div>
            <button
              type="button"
              onClick={() => onChange({ ...config, filler_words: !config.filler_words })}
              className={`w-12 h-6 rounded-full transition-colors ${config.filler_words ? 'bg-black' : 'bg-gray-300'}`}
            >
              <div className={`w-5 h-5 rounded-full bg-white transition-transform ${config.filler_words ? 'translate-x-6' : 'translate-x-1'}`} />
            </button>
          </div>
        </div>
  
        <div>
          <label className="block font-semibold mb-2">
            Interruption Sensitivity: {config.interruption_sensitivity}%
          </label>
          <input
            type="range"
            min="0"
            max="100"
            value={config.interruption_sensitivity}
            onChange={(e) => onChange({ ...config, interruption_sensitivity: parseInt(e.target.value) })}
            className="w-full h-2 bg-gray-200 appearance-none cursor-pointer"
            style={{
              background: `linear-gradient(to right, black 0%, black ${config.interruption_sensitivity}%, #e5e7eb ${config.interruption_sensitivity}%, #e5e7eb 100%)`
            }}
          />
          <div className="flex justify-between text-xs text-gray-600 mt-1">
            <span>Less sensitive</span>
            <span>More sensitive</span>
          </div>
        </div>
  
        <div className="flex gap-3">
          <button
            onClick={onSubmit}
            disabled={isLoading}
            className="flex-1 bg-black text-white py-3 px-6 font-bold hover:bg-gray-800 transition-colors disabled:bg-gray-400"
          >
            {isLoading ? 'Saving...' : isEditing ? 'Update Configuration' : 'Save Configuration'}
          </button>
          {isEditing && onCancel && (
            <button
              onClick={onCancel}
              className="px-6 py-3 border-2 border-black font-bold hover:bg-gray-100"
            >
              Cancel
            </button>
          )}
        </div>
      </div>
    );
  };