import { useState, useCallback } from "react";
import { apiService } from "../services/api";
import { AgentConfig, AgentConfigCreate } from "../types";

export default function useAgentConfigs() {
    const [configs, setConfigs] = useState<AgentConfig[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
  
    const loadConfigs = useCallback(async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await apiService.listAgentConfigs();
        setConfigs(data);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to load configurations';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    }, []);
  
    const createConfig = useCallback(async (data: AgentConfigCreate) => {
      const newConfig = await apiService.createAgentConfig(data);
      setConfigs(prev => [...prev, newConfig]);
      return newConfig;
    }, []);
  
    const updateConfig = useCallback(async (id: string, data: Partial<AgentConfigCreate>) => {
      const updated = await apiService.updateAgentConfig(id, data);
      setConfigs(prev => prev.map(c => c.id === id ? updated : c));
      return updated;
    }, []);
  
    const deleteConfig = useCallback(async (id: string) => {
      await apiService.deleteAgentConfig(id);
      setConfigs(prev => prev.filter(c => c.id !== id));
    }, []);
  
    return {
      configs,
      loading,
      error,
      loadConfigs,
      createConfig,
      updateConfig,
      deleteConfig,
    };
  }