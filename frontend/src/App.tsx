import React, { useEffect, useState } from "react";
import "./App.css";
import { Settings, Phone, FileText } from "lucide-react";
import { CallDetails } from "./components/CallDetails";
import { CallList } from "./components/CallList";
import { CallTriggerForm } from "./components/CallTriggerForm";
import { ConfigForm } from "./components/ConfigForm";
import { ConfigList } from "./components/ConfigList";
import { NotificationBanner } from "./components/NotificationBanner";
import useAgentConfigs from "./hooks/useAgentConfigs";
import useCalls from "./hooks/useCalls";
import { AppNotification } from "./types";
import {
  TabType,
  AgentConfigCreate,
  CallRequest,
  Call,
  CallResult,
  AgentConfig,
} from "./types";
import { useNotifications } from "./hooks/useNotification";

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>("config");

  // Use custom hooks
  const {
    configs,
    loading: configsLoading,
    loadConfigs,
    createConfig,
    updateConfig,
    deleteConfig,
  } = useAgentConfigs();
  const {
    calls,
    callResults,
    loading: callsLoading,
    loadCalls,
    createCall,
    refreshCallStatus,
    getCallResult,
  } = useCalls();
  const { notification, showNotification, clearNotification } =
    useNotifications();

  // Local state
  const [currentConfig, setCurrentConfig] = useState<AgentConfigCreate>({
    name: "",
    system_prompt: "",
    backchanneling: true,
    filler_words: true,
    interruption_sensitivity: 50,
    scenario_type: "check-in",
  });
  const [editingConfigId, setEditingConfigId] = useState<string | null>(null);
  const [callRequest, setCallRequest] = useState<CallRequest>({
    driver_name: "",
    phone_number: "",
    load_number: "",
    agent_config_id: "",
  });
  const [selectedCall, setSelectedCall] = useState<Call | null>(null);
  const [selectedResult, setSelectedResult] = useState<CallResult | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Load initial data
  useEffect(() => {
    loadConfigs().catch((err) => {
      showNotification(
        "error",
        `Failed to load configurations: ${err.message}`
      );
    });
  }, []);

  // Load calls when results tab is active
  useEffect(() => {
    if (activeTab === "results") {
      loadCalls().catch((err) => {
        showNotification("error", `Failed to load calls: ${err.message}`);
      });
    }
  }, [activeTab]);

  // Auto-refresh calls in progress
  useEffect(() => {
    const inProgressCalls = calls.filter(
      (c) => c.status === "pending" || c.status === "in_progress"
    );

    if (inProgressCalls.length > 0 && activeTab === "results") {
      const interval = setInterval(() => {
        inProgressCalls.forEach((call) => {
          refreshCallStatus(call.id).catch((err) =>
            console.error("Failed to refresh:", err)
          );
        });
      }, 3000);

      return () => clearInterval(interval);
    }
  }, [calls, activeTab, refreshCallStatus]);

  // Handlers
  const handleSaveConfig = async () => {
    if (!currentConfig.name || !currentConfig.system_prompt) {
      showNotification("error", "Please fill in all required fields");
      return;
    }

    setIsSubmitting(true);
    try {
      if (editingConfigId) {
        await updateConfig(editingConfigId, currentConfig);
        showNotification("success", "Configuration updated successfully");
        setEditingConfigId(null);
      } else {
        await createConfig(currentConfig);
        showNotification("success", "Configuration created successfully");
      }

      setCurrentConfig({
        name: "",
        system_prompt: "",
        backchanneling: true,
        filler_words: true,
        interruption_sensitivity: 50,
        scenario_type: "check-in",
      });
    } catch (error) {
      showNotification(
        "error",
        `Failed to save configuration: ${
          error instanceof Error ? error.message : "Unknown error"
        }`
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEditConfig = (config: AgentConfig) => {
    setCurrentConfig({
      name: config.name,
      system_prompt: config.system_prompt,
      backchanneling: config.backchanneling,
      filler_words: config.filler_words,
      interruption_sensitivity: config.interruption_sensitivity,
      scenario_type: config.scenario_type,
    });
    setEditingConfigId(config.id);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleCancelEdit = () => {
    setEditingConfigId(null);
    setCurrentConfig({
      name: "",
      system_prompt: "",
      backchanneling: true,
      filler_words: true,
      interruption_sensitivity: 50,
      scenario_type: "check-in",
    });
  };

  const handleStartCall = async () => {
    if (
      !callRequest.driver_name ||
      !callRequest.phone_number ||
      !callRequest.load_number ||
      !callRequest.agent_config_id
    ) {
      showNotification("error", "Please fill in all call details");
      return;
    }

    setIsSubmitting(true);
    try {
      await createCall(callRequest);
      showNotification(
        "success",
        "Call initiated successfully! Check results tab for status."
      );

      setCallRequest({
        driver_name: "",
        phone_number: "",
        load_number: "",
        agent_config_id: "",
      });

      setActiveTab("results");
    } catch (error) {
      showNotification(
        "error",
        `Failed to start call: ${
          error instanceof Error ? error.message : "Unknown error"
        }`
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleStartWebCall = async (request: CallRequest): Promise<Call> => {
    try {
      const call = await createCall(request);

      if (!call.access_token) {
        throw new Error("No access token received from API");
      }

      showNotification("success", "Web call created successfully!");
      return call;
    } catch (error) {
      showNotification(
        "error",
        `Failed to create web call: ${
          error instanceof Error ? error.message : "Unknown error"
        }`
      );
      throw error;
    }
  };

  const handleViewCallDetails = async (call: Call) => {
    setSelectedCall(call);
    setSelectedResult(null);

    if (call.status === "completed") {
      try {
        const result = await getCallResult(call.id);
        setSelectedResult(result);
      } catch (error) {
        showNotification("error", "Failed to load call result");
      }
    }
  };

  const handleRefreshCallDetails = async () => {
    if (!selectedCall) return;

    try {
      const updated = await refreshCallStatus(selectedCall.id);
      setSelectedCall(updated);

      if (updated.status === "completed") {
        const result = await getCallResult(updated.id);
        setSelectedResult(result);
      }
    } catch (error) {
      showNotification("error", "Failed to refresh call details");
    }
  };

  // Render tabs
  const renderConfigTab = () => (
    <div className="space-y-6">
      <div className="bg-white border-2 border-black p-6">
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <Settings className="w-6 h-6" />
          {editingConfigId
            ? "Edit Agent Configuration"
            : "Create Agent Configuration"}
        </h2>
        <ConfigForm
          config={currentConfig}
          onChange={setCurrentConfig}
          onSubmit={handleSaveConfig}
          onCancel={editingConfigId ? handleCancelEdit : undefined}
          isEditing={!!editingConfigId}
          isLoading={isSubmitting}
        />
      </div>
      <ConfigList
        configs={configs}
        onEdit={handleEditConfig}
        onDelete={() => null}
        onRefresh={loadConfigs}
        isLoading={configsLoading}
      />
    </div>
  );

  const renderCallTab = () => (
    <div className="bg-white border-2 border-black p-6">
      <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
        <Phone className="w-6 h-6" />
        Trigger Test Call
      </h2>
      <CallTriggerForm
        request={callRequest}
        onChange={setCallRequest}
        onSubmit={handleStartCall}
        onWebCallSubmit={handleStartWebCall}
        configs={configs}
        isLoading={isSubmitting}
      />
    </div>
  );

  const renderResultsTab = () => (
    <div className="space-y-6">
      <CallList
        calls={calls}
        onSelect={handleViewCallDetails}
        onRefresh={loadCalls}
        isLoading={callsLoading}
      />
      {selectedCall && (
        <CallDetails
          call={selectedCall}
          result={selectedResult}
          onClose={() => {
            setSelectedCall(null);
            setSelectedResult(null);
          }}
          onRefresh={handleRefreshCallDetails}
        />
      )}
    </div>
  );

  // Count active calls
  const activeCallsCount = calls.filter(
    (c) => c.status === "in_progress" || c.status === "pending"
  ).length;

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-black text-white p-6 border-b-4 border-white">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold">AI Voice Agent Admin Dashboard</h1>
          <p className="text-gray-300 mt-1">
            Configure, test, and review logistics voice agents
          </p>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b-4 border-black">
        <div className="max-w-7xl mx-auto flex">
          <button
            onClick={() => setActiveTab("config")}
            className={`flex-1 py-4 px-6 font-bold transition-colors ${
              activeTab === "config"
                ? "bg-black text-white"
                : "hover:bg-gray-100"
            }`}
          >
            <Settings className="w-5 h-5 inline mr-2" />
            Configure Agent
          </button>
          <button
            onClick={() => setActiveTab("call")}
            className={`flex-1 py-4 px-6 font-bold transition-colors border-l-2 border-r-2 border-black ${
              activeTab === "call" ? "bg-black text-white" : "hover:bg-gray-100"
            }`}
          >
            <Phone className="w-5 h-5 inline mr-2" />
            Trigger Call
          </button>
          <button
            onClick={() => setActiveTab("results")}
            className={`flex-1 py-4 px-6 font-bold transition-colors ${
              activeTab === "results"
                ? "bg-black text-white"
                : "hover:bg-gray-100"
            }`}
          >
            <FileText className="w-5 h-5 inline mr-2" />
            View Results
            {activeCallsCount > 0 && (
              <span className="ml-2 px-2 py-1 bg-yellow-500 text-black text-xs font-bold rounded-full">
                {activeCallsCount}
              </span>
            )}
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto p-6">
        {activeTab === "config" && renderConfigTab()}
        {activeTab === "call" && renderCallTab()}
        {activeTab === "results" && renderResultsTab()}
      </main>

      {/* Footer */}
      <footer className="bg-black text-white text-center p-4 mt-12 border-t-4 border-white">
        <p className="text-sm">
          AI Voice Agent Tool - Logistics Management System
        </p>
        <p className="text-xs text-gray-400 mt-1">
          Built with React, TypeScript, FastAPI & Retell AI
        </p>
      </footer>
    </div>
  );
};

export default App;
