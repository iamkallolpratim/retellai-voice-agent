import { FileText, RefreshCw } from "lucide-react";
import { Call } from "../types";
import { StatusBadge } from "./StatusBadge";

export const CallList: React.FC<{
    calls: Call[];
    onSelect: (call: Call) => void;
    onRefresh: () => void;
    isLoading: boolean;
  }> = ({ calls, onSelect, onRefresh, isLoading }) => {
    return (
      <div className="bg-white border-2 border-black p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <FileText className="w-6 h-6" />
            Call Results
          </h2>
          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="px-4 py-2 border-2 border-black hover:bg-gray-100 transition-colors disabled:opacity-50 flex items-center gap-2 font-semibold"
          >
            <RefreshCw className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
  
        {isLoading ? (
          <div className="text-center py-8 text-gray-500">Loading calls...</div>
        ) : calls.length === 0 ? (
          <p className="text-gray-500 text-center py-8">
            No call results yet. Trigger a test call to see results here.
          </p>
        ) : (
          <div className="space-y-3">
            {calls.map((call) => (
              <div
                key={call.id}
                onClick={() => onSelect(call)}
                className="p-4 border-2 border-black cursor-pointer hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="font-bold text-lg">
                      {call.driver_name} - Load {call.load_number}
                    </div>
                    <div className="text-sm text-gray-600 mt-1">
                      {new Date(call.created_at).toLocaleString()}
                    </div>
                    {call.completed_at && (
                      <div className="text-xs text-gray-500 mt-1">
                        Completed: {new Date(call.completed_at).toLocaleString()}
                      </div>
                    )}
                  </div>
                  <StatusBadge status={call.status} />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };