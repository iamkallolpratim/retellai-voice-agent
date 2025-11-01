import { RefreshCw, Truck, Clock, AlertCircle } from "lucide-react";
import { Call, CallResult } from "../types";
import { StatusBadge } from "./StatusBadge";

export const CallDetails: React.FC<{
    call: Call;
    result: CallResult | null;
    onClose: () => void;
    onRefresh: () => void;
  }> = ({ call, result, onClose, onRefresh }) => {
    return (
      <div className="bg-white border-2 border-black p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold">Call Details</h3>
          <div className="flex gap-2">
            <button
              onClick={onRefresh}
              className="px-3 py-2 border-2 border-black hover:bg-gray-100 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
            <StatusBadge status={call.status} />
          </div>
        </div>
  
        <div className="space-y-4 mb-6">
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 border border-black">
              <div className="text-sm text-gray-600 font-semibold">Driver</div>
              <div className="font-bold mt-1">{call.driver_name}</div>
            </div>
            <div className="p-3 border border-black">
              <div className="text-sm text-gray-600 font-semibold">Load Number</div>
              <div className="font-bold mt-1">{call.load_number}</div>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 border border-black">
              <div className="text-sm text-gray-600 font-semibold">Phone Number</div>
              <div className="font-bold mt-1">{call.phone_number}</div>
            </div>
            <div className="p-3 border border-black">
              <div className="text-sm text-gray-600 font-semibold">Call ID</div>
              <div className="font-bold mt-1 text-xs font-mono">{call.id}</div>
            </div>
          </div>
        </div>
  
        {call.status === 'completed' && result ? (
          <>
            <div className="mb-6">
              <h4 className="font-bold text-lg mb-3 flex items-center gap-2">
                <Truck className="w-5 h-5" />
                Structured Data
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {Object.entries(result.structured_data).map(([key, value]) => (
                  <div key={key} className="p-3 border border-black">
                    <div className="text-sm text-gray-600 font-semibold uppercase tracking-wide">
                      {key.replace(/_/g, ' ')}
                    </div>
                    <div className="font-bold mt-1">
                      {typeof value === 'boolean' ? (value ? '✓ Yes' : '✗ No') : value || 'N/A'}
                    </div>
                  </div>
                ))}
              </div>
              {result.call_duration && (
                <div className="mt-3 p-3 border border-black bg-gray-50">
                  <div className="text-sm text-gray-600 font-semibold">Call Duration</div>
                  <div className="font-bold mt-1">
                    {Math.floor(result.call_duration / 60)}m {result.call_duration % 60}s
                  </div>
                </div>
              )}
            </div>
  
            <div>
              <h4 className="font-bold text-lg mb-3">Full Transcript</h4>
              <div className="p-4 border-2 border-black bg-gray-50 whitespace-pre-wrap font-mono text-sm max-h-96 overflow-y-auto">
                {result.transcript || 'Transcript not available'}
              </div>
            </div>
          </>
        ) : call.status === 'in_progress' || call.status === 'pending' ? (
          <div className="text-center py-8">
            <Clock className="w-12 h-12 mx-auto mb-4 animate-spin" />
            <p className="text-gray-600 font-semibold">
              Call is {call.status === 'pending' ? 'pending' : 'in progress'}...
            </p>
            <p className="text-sm text-gray-500 mt-2">
              Results will appear here when the call completes
            </p>
          </div>
        ) : call.status === 'failed' ? (
          <div className="text-center py-8">
            <AlertCircle className="w-12 h-12 mx-auto mb-4 text-red-600" />
            <p className="text-red-600 font-semibold">Call failed</p>
            <p className="text-sm text-gray-500 mt-2">
              Please check the call configuration and try again
            </p>
          </div>
        ) : null}
  
        <button
          onClick={onClose}
          className="mt-6 w-full bg-black text-white py-3 px-6 font-bold hover:bg-gray-800 transition-colors"
        >
          Close Details
        </button>
      </div>
    );
  };
  