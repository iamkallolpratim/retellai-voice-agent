import { useState, useCallback } from "react";
import { apiService } from "../services/api";
import { Call, CallResult, CallRequest } from "../types";

export default function useCalls() {
    const [calls, setCalls] = useState<Call[]>([]);
    const [callResults, setCallResults] = useState<Map<string, CallResult>>(new Map());
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
  
    const loadCalls = useCallback(async (limit = 50, offset = 0) => {
      setLoading(true);
      setError(null);
      try {
        const data = await apiService.listCalls(limit, offset);
        setCalls(data);
        
        // Load results for completed calls
        const completedCalls = data.filter(c => c.status === 'completed');
        for (const call of completedCalls) {
          try {
            const result = await apiService.getCallResult(call.id);
            setCallResults(prev => new Map(prev).set(call.id, result));
          } catch (err) {
            console.log(`No result yet for call ${call.id}`);
          }
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to load calls';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    }, []);
  
    const createCall = useCallback(async (data: CallRequest) => {
      const newCall = await apiService.createCall(data);
      setCalls(prev => [newCall, ...prev]);
      return newCall;
    }, []);
  
    const refreshCallStatus = useCallback(async (callId: string) => {
      try {
        const updated = await apiService.getCallStatus(callId);
        setCalls(prev => prev.map(c => c.id === callId ? updated : c));
        
        if (updated.status === 'completed' && !callResults.has(callId)) {
          try {
            const result = await apiService.getCallResult(callId);
            setCallResults(prev => new Map(prev).set(callId, result));
          } catch (err) {
            console.log(`Result not yet available for call ${callId}`);
          }
        }
        
        return updated;
      } catch (err) {
        console.error(`Failed to refresh call status: ${err}`);
        throw err;
      }
    }, [callResults]);
  
    const getCallResult = useCallback(async (callId: string) => {
      if (callResults.has(callId)) {
        return callResults.get(callId)!;
      }
      
      const result = await apiService.getCallResult(callId);
      setCallResults(prev => new Map(prev).set(callId, result));
      return result;
    }, [callResults]);
  
    return {
      calls,
      callResults,
      loading,
      error,
      loadCalls,
      createCall,
      refreshCallStatus,
      getCallResult,
    };
  }