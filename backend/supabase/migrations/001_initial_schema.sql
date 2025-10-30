-- supabase/migrations/001_initial_schema.sql
-- AI Voice Agent Database Schema

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==================== Agent Configurations Table ====================
CREATE TABLE agent_configurations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    scenario_type VARCHAR(50) NOT NULL CHECK (scenario_type IN ('driver_checkin', 'emergency_protocol')),
    system_prompt TEXT NOT NULL,
    retell_agent_id VARCHAR(255),  -- Retell AI agent ID
    backchanneling BOOLEAN DEFAULT true,
    interruption_sensitivity FLOAT DEFAULT 0.7 CHECK (interruption_sensitivity >= 0 AND interruption_sensitivity <= 1),
    filler_words BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for faster queries
CREATE INDEX idx_agent_configurations_scenario ON agent_configurations(scenario_type);
CREATE INDEX idx_agent_configurations_created ON agent_configurations(created_at DESC);

-- ==================== Calls Table ====================
CREATE TABLE calls (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_config_id UUID NOT NULL REFERENCES agent_configurations(id) ON DELETE CASCADE,
    driver_name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    load_number VARCHAR(50) NOT NULL,
    retell_call_id VARCHAR(255) UNIQUE,  -- Retell AI call ID
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for faster queries
CREATE INDEX idx_calls_agent_config ON calls(agent_config_id);
CREATE INDEX idx_calls_status ON calls(status);
CREATE INDEX idx_calls_retell_id ON calls(retell_call_id);
CREATE INDEX idx_calls_created ON calls(created_at DESC);
CREATE INDEX idx_calls_load_number ON calls(load_number);

-- ==================== Call Results Table ====================
CREATE TABLE call_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    call_id UUID NOT NULL REFERENCES calls(id) ON DELETE CASCADE,
    call_outcome VARCHAR(100),
    structured_data JSONB NOT NULL,  -- Flexible JSON storage for different scenario types
    full_transcript TEXT NOT NULL,
    duration INTEGER DEFAULT 0,  -- Duration in seconds
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for faster queries
CREATE INDEX idx_call_results_call_id ON call_results(call_id);
CREATE INDEX idx_call_results_outcome ON call_results(call_outcome);
CREATE INDEX idx_call_results_structured_data ON call_results USING GIN (structured_data);  -- For JSON queries

-- ==================== Update Trigger for updated_at ====================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_agent_configurations_updated_at 
    BEFORE UPDATE ON agent_configurations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ==================== Sample Data for Testing ====================
-- Insert a sample driver check-in agent
INSERT INTO agent_configurations (
    name,
    scenario_type,
    system_prompt,
    backchanneling,
    interruption_sensitivity,
    filler_words
) VALUES (
    'Driver Check-in Agent',
    'driver_checkin',
    'You are a professional dispatch agent conducting routine check-in calls with drivers.',
    true,
    0.7,
    true
);

-- Insert a sample emergency protocol agent
INSERT INTO agent_configurations (
    name,
    scenario_type,
    system_prompt,
    backchanneling,
    interruption_sensitivity,
    filler_words
) VALUES (
    'Emergency Response Agent',
    'emergency_protocol',
    'You are handling emergency calls from drivers. Prioritize safety and gather critical information quickly.',
    true,
    0.8,  -- Higher sensitivity for emergencies
    false  -- No filler words in emergencies
);

-- ==================== Views for Analytics ====================
-- View for call statistics by agent
CREATE VIEW agent_call_stats AS
SELECT 
    ac.id as agent_id,
    ac.name as agent_name,
    ac.scenario_type,
    COUNT(c.id) as total_calls,
    COUNT(CASE WHEN c.status = 'completed' THEN 1 END) as completed_calls,
    COUNT(CASE WHEN c.status = 'failed' THEN 1 END) as failed_calls,
    AVG(CASE WHEN cr.duration > 0 THEN cr.duration END) as avg_duration_seconds
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
    cr.call_outcome,
    cr.structured_data,
    cr.duration
FROM calls c
JOIN agent_configurations ac ON ac.id = c.agent_config_id
LEFT JOIN call_results cr ON cr.call_id = c.id
ORDER BY c.created_at DESC;

-- ==================== Comments for Documentation ====================
COMMENT ON TABLE agent_configurations IS 'Stores AI agent configurations including prompts and voice settings';
COMMENT ON TABLE calls IS 'Tracks all phone calls made by the system';
COMMENT ON TABLE call_results IS 'Stores structured results and transcripts from completed calls';
COMMENT ON COLUMN call_results.structured_data IS 'JSON object containing extracted data specific to the scenario type';
COMMENT ON COLUMN calls.status IS 'Call status: pending (not started), in_progress (active), completed (finished), failed (error)';
