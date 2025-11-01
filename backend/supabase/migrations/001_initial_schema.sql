-- supabase/migrations/001_initial_schema.sql
-- AI Voice Agent Database Schema

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==================== Agent Configurations Table ====================
CREATE TABLE IF NOT EXISTS agent_configurations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    scenario_type VARCHAR(50) NOT NULL CHECK (scenario_type IN ('check-in', 'emergency')),
    system_prompt TEXT NOT NULL,
    retell_agent_id VARCHAR(255),  -- Retell AI agent ID
    backchanneling BOOLEAN DEFAULT true,
    interruption_sensitivity INTEGER DEFAULT 50 CHECK (interruption_sensitivity >= 0 AND interruption_sensitivity <= 100),
    filler_words BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_agent_configurations_scenario ON agent_configurations(scenario_type);
CREATE INDEX IF NOT EXISTS idx_agent_configurations_created ON agent_configurations(created_at DESC);

-- ==================== Calls Table ====================
CREATE TABLE IF NOT EXISTS calls (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_config_id UUID NOT NULL REFERENCES agent_configurations(id) ON DELETE CASCADE,
    driver_name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    load_number VARCHAR(50) NOT NULL,
    retell_call_id VARCHAR(255) UNIQUE,  -- Retell AI call ID
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_calls_agent_config ON calls(agent_config_id);
CREATE INDEX IF NOT EXISTS idx_calls_status ON calls(status);
CREATE INDEX IF NOT EXISTS idx_calls_retell_id ON calls(retell_call_id);
CREATE INDEX IF NOT EXISTS idx_calls_created ON calls(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_calls_load_number ON calls(load_number);

-- ==================== Call Results Table ====================
CREATE TABLE IF NOT EXISTS call_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    call_id UUID NOT NULL REFERENCES calls(id) ON DELETE CASCADE UNIQUE,
    full_transcript TEXT,  -- Changed from NOT NULL to allow gradual updates
    structured_data JSONB,  -- Changed from NOT NULL for flexibility
    call_duration INTEGER DEFAULT 0,  -- Duration in seconds
    call_summary TEXT,  -- From Retell analysis
    user_sentiment VARCHAR(50),  -- From Retell analysis
    call_successful BOOLEAN,  -- From Retell analysis
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_call_results_call_id ON call_results(call_id);
CREATE INDEX IF NOT EXISTS idx_call_results_structured_data ON call_results USING GIN (structured_data);  -- For JSON queries

-- ==================== Update Trigger for updated_at ====================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Drop existing triggers if they exist
DROP TRIGGER IF EXISTS update_agent_configurations_updated_at ON agent_configurations;
DROP TRIGGER IF EXISTS update_calls_updated_at ON calls;
DROP TRIGGER IF EXISTS update_call_results_updated_at ON call_results;

-- Create triggers
CREATE TRIGGER update_agent_configurations_updated_at 
    BEFORE UPDATE ON agent_configurations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_calls_updated_at 
    BEFORE UPDATE ON calls
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_call_results_updated_at 
    BEFORE UPDATE ON call_results
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ==================== Sample Data for Testing ====================
-- Insert sample agents only if table is empty
INSERT INTO agent_configurations (
    name,
    scenario_type,
    system_prompt,
    backchanneling,
    interruption_sensitivity,
    filler_words
)
SELECT 
    'Driver Check-in Agent',
    'check-in',
    'You are a professional dispatch agent conducting routine check-in calls with drivers. Start with: "Hi {driver_name}, this is Dispatch with a check call on load {load_number}. Can you give me an update on your status?" Based on their response, ask follow-up questions about location, ETA, or unloading status. Always remind them to submit their POD. If they mention any emergency, immediately switch to safety protocol.',
    true,
    50,
    true
WHERE NOT EXISTS (SELECT 1 FROM agent_configurations WHERE name = 'Driver Check-in Agent');

INSERT INTO agent_configurations (
    name,
    scenario_type,
    system_prompt,
    backchanneling,
    interruption_sensitivity,
    filler_words
)
SELECT
    'Emergency Response Agent',
    'emergency',
    'You are handling emergency calls from drivers. If the driver mentions accident, breakdown, medical issue, or any emergency: 1. Ask: "Are you safe? Is anyone injured?" 2. Ask: "What is your exact location?" 3. Ask: "Is your load secure?" 4. Say: "I am connecting you to a human dispatcher right away."',
    true,
    80,  -- Higher sensitivity for emergencies
    false  -- No filler words in emergencies
WHERE NOT EXISTS (SELECT 1 FROM agent_configurations WHERE name = 'Emergency Response Agent');

-- ==================== Views for Analytics ====================
-- Drop existing views if they exist
DROP VIEW IF EXISTS agent_call_stats;
DROP VIEW IF EXISTS recent_calls_with_results;

-- View for call statistics by agent
CREATE VIEW agent_call_stats AS
SELECT 
    ac.id as agent_id,
    ac.name as agent_name,
    ac.scenario_type,
    COUNT(c.id) as total_calls,
    COUNT(CASE WHEN c.status = 'completed' THEN 1 END) as completed_calls,
    COUNT(CASE WHEN c.status = 'failed' THEN 1 END) as failed_calls,
    AVG(CASE WHEN cr.call_duration > 0 THEN cr.call_duration END) as avg_duration_seconds
FROM agent_configurations ac
LEFT JOIN calls c ON c.agent_config_id = ac.id
LEFT JOIN call_results cr ON cr.call_id = c.id
GROUP BY ac.id, ac.name, ac.scenario_type;

-- View for recent calls with results
CREATE VIEW recent_calls_with_results AS
SELECT 
    c.id as call_id,
    c.driver_name,
    c.phone_number,
    c.load_number,
    c.status,
    c.created_at as call_created_at,
    c.completed_at,
    ac.name as agent_name,
    ac.scenario_type,
    cr.structured_data,
    cr.call_duration,
    cr.call_summary,
    cr.user_sentiment
FROM calls c
JOIN agent_configurations ac ON ac.id = c.agent_config_id
LEFT JOIN call_results cr ON cr.call_id = c.id
ORDER BY c.created_at DESC;

-- ==================== Comments for Documentation ====================
COMMENT ON TABLE agent_configurations IS 'Stores AI agent configurations including prompts and voice settings';
COMMENT ON TABLE calls IS 'Tracks all phone calls made by the system';
COMMENT ON TABLE call_results IS 'Stores structured results and transcripts from completed calls';
COMMENT ON COLUMN call_results.structured_data IS 'JSON object containing extracted data specific to the scenario type (check-in or emergency)';
COMMENT ON COLUMN calls.status IS 'Call status: pending (not started), in_progress (active), completed (finished), failed (error)';
COMMENT ON COLUMN agent_configurations.interruption_sensitivity IS 'Interruption sensitivity from 0-100, where higher values make the agent more sensitive to interruptions';
COMMENT ON COLUMN agent_configurations.scenario_type IS 'Type of scenario: check-in (routine driver check) or emergency (emergency protocol)';