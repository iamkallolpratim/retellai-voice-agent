import { RefreshCw, Trash2 } from "lucide-react";
import { AgentConfig } from "../types";

export const ConfigList: React.FC<{
    configs: AgentConfig[];
    onEdit: (config: AgentConfig) => void;
    onDelete: (id: string) => void;
    onRefresh: () => void;
    isLoading: boolean;
  }> = ({ configs, onEdit, onDelete, onRefresh, isLoading }) => {
    return (
      <div className="bg-white border-2 border-black p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold">Saved Configurations</h3>
          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="p-2 border-2 border-black hover:bg-gray-100 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
  
        <div className="space-y-3">
          {isLoading ? (
            <div className="text-center py-8 text-gray-500">Loading configurations...</div>
          ) : configs.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No configurations saved yet</p>
          ) : (
            configs.map((config) => (
              <div key={config.id} className="p-4 border-2 border-black hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="font-bold text-lg">{config.name}</div>
                    <div className="text-sm text-gray-600 mt-1">
                      {config.scenario_type === 'check-in' ? '📋 Check-in' : '🚨 Emergency'} Scenario
                    </div>
                    {config.retell_agent_id && (
                      <div className="text-xs text-gray-500 mt-1 font-mono">
                        Agent ID: {config.retell_agent_id}
                      </div>
                    )}
                    <div className="text-xs text-gray-500 mt-1">
                      Created: {new Date(config.created_at || '').toLocaleString()}
                    </div>
                  </div>
                  <div className="flex gap-2 ml-4">
                    <button
                      onClick={() => onEdit(config)}
                      className="px-3 py-1 border-2 border-black hover:bg-black hover:text-white transition-colors text-sm font-semibold"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => onDelete(config.id)}
                      className="px-3 py-1 border-2 border-red-600 text-red-600 hover:bg-red-600 hover:text-white transition-colors text-sm font-semibold"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    );
  };