-- ============================================================
-- Template Customization & Output Restrictions - Database Schema
-- ============================================================
-- This migration adds three tables for user preferences, templates,
-- and content restrictions.
--
-- Execute this in your Supabase SQL Editor to set up the tables.
-- ============================================================

-- ============================================================
-- 1. Create proposal_templates Table
-- ============================================================
-- Stores pre-defined template variants (Technical, Consultative, Quick Win)
CREATE TABLE IF NOT EXISTS proposal_templates (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    template_type TEXT NOT NULL CHECK (template_type IN ('technical', 'consultative', 'quick_win')),
    structure_config JSONB NOT NULL DEFAULT '{}'::JSONB,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for template type queries
CREATE INDEX IF NOT EXISTS idx_proposal_templates_type
ON proposal_templates (template_type);

-- Comment on table
COMMENT ON TABLE proposal_templates IS 'Pre-defined proposal template variants for customization';
COMMENT ON COLUMN proposal_templates.structure_config IS 'JSONB config with section weights, emphasis areas';


-- ============================================================
-- 2. Create tone_presets Table
-- ============================================================
-- Stores tone/style configurations (professional, conversational, technical, friendly)
CREATE TABLE IF NOT EXISTS tone_presets (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    tone_type TEXT NOT NULL CHECK (tone_type IN ('professional', 'conversational', 'technical', 'friendly')),
    language_patterns JSONB NOT NULL DEFAULT '{}'::JSONB,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for tone type queries
CREATE INDEX IF NOT EXISTS idx_tone_presets_type
ON tone_presets (tone_type);

-- Comment on table
COMMENT ON TABLE tone_presets IS 'Tone and style presets for language modification';
COMMENT ON COLUMN tone_presets.language_patterns IS 'JSONB config for formality level, vocabulary choices';


-- ============================================================
-- 3. Create content_restrictions Table
-- ============================================================
-- Stores user-specific content filtering rules
CREATE TABLE IF NOT EXISTS content_restrictions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL,
    forbidden_phrases JSONB DEFAULT '[]'::JSONB,
    required_elements JSONB DEFAULT '[]'::JSONB,
    word_count_overrides JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Index for user queries
CREATE INDEX IF NOT EXISTS idx_content_restrictions_user
ON content_restrictions (user_id);

-- GIN index for JSONB searches
CREATE INDEX IF NOT EXISTS idx_content_restrictions_forbidden
ON content_restrictions USING GIN (forbidden_phrases);

CREATE INDEX IF NOT EXISTS idx_content_restrictions_required
ON content_restrictions USING GIN (required_elements);

-- Comment on table
COMMENT ON TABLE content_restrictions IS 'User-specific content filtering and validation rules';
COMMENT ON COLUMN content_restrictions.forbidden_phrases IS 'JSONB array of phrases to block';
COMMENT ON COLUMN content_restrictions.required_elements IS 'JSONB array of required patterns (regex supported)';
COMMENT ON COLUMN content_restrictions.word_count_overrides IS 'JSONB object with custom word count ranges';


-- ============================================================
-- 4. Create user_preferences Table
-- ============================================================
-- Stores user's selected template, tone, and restriction references
CREATE TABLE IF NOT EXISTS user_preferences (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL UNIQUE,
    template_id TEXT NOT NULL REFERENCES proposal_templates(id) ON DELETE SET DEFAULT,
    tone_id TEXT NOT NULL REFERENCES tone_presets(id) ON DELETE SET DEFAULT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for user queries (primary lookup pattern)
CREATE INDEX IF NOT EXISTS idx_user_preferences_user
ON user_preferences (user_id);

-- Comment on table
COMMENT ON TABLE user_preferences IS 'User-specific template and tone selections';
COMMENT ON COLUMN user_preferences.template_id IS 'Foreign key to proposal_templates';
COMMENT ON COLUMN user_preferences.tone_id IS 'Foreign key to tone_presets';


-- ============================================================
-- 5. Add Triggers for updated_at Timestamp
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_proposal_templates_updated_at
    BEFORE UPDATE ON proposal_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tone_presets_updated_at
    BEFORE UPDATE ON tone_presets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_content_restrictions_updated_at
    BEFORE UPDATE ON content_restrictions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at
    BEFORE UPDATE ON user_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
