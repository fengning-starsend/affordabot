-- ============================================================================
-- Add Pipeline Runs Table
-- Migration: 20251213_add_pipeline_runs.sql
--
-- Creates table for:
-- - Tracking individual analysis pipeline runs
-- - Storing detailed run status, models used, and errors
-- ============================================================================

CREATE TABLE IF NOT EXISTS pipeline_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bill_id VARCHAR(255) NOT NULL,
    jurisdiction VARCHAR(100),
    status VARCHAR(50) NOT NULL DEFAULT 'running' CHECK (status IN ('running', 'completed', 'failed')),

    -- Configuration
    models JSONB,

    -- Results
    result JSONB,
    error_message TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Index for querying runs by bill
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_bill_id
    ON pipeline_runs(bill_id, created_at DESC);

-- Trigger for updated_at
DROP TRIGGER IF EXISTS update_pipeline_runs_updated_at ON pipeline_runs;
CREATE TRIGGER update_pipeline_runs_updated_at
    BEFORE UPDATE ON pipeline_runs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE pipeline_runs IS 'Tracks individual executions of the analysis pipeline';
COMMENT ON COLUMN pipeline_runs.models IS 'JSON object mapping step names to model names';
COMMENT ON COLUMN pipeline_runs.result IS 'Final output of the pipeline (e.g. analysis summary)';

-- Enable RLS
ALTER TABLE pipeline_runs ENABLE ROW LEVEL SECURITY;

-- Policies (same as other tables)
DROP POLICY IF EXISTS "Admin full access to pipeline_runs" ON pipeline_runs;
CREATE POLICY "Admin full access to pipeline_runs"
    ON pipeline_runs
    FOR ALL
    USING (true)
    WITH CHECK (true);

GRANT SELECT, INSERT, UPDATE ON pipeline_runs TO authenticated;
GRANT ALL ON pipeline_runs TO service_role;
