-- ============================================================
-- Seed Default Templates and Tone Presets
-- ============================================================
-- This migration inserts default template and tone data.
--
-- Execute AFTER 001_add_user_preferences.sql
-- ============================================================

-- ============================================================
-- 1. Insert Proposal Templates
-- ============================================================

INSERT INTO proposal_templates (id, name, template_type, structure_config, description)
VALUES
(
    'technical-001',
    'Technical',
    'technical',
    '{"emphasis": "solution_depth", "technical_detail": "high", "section_weights": {"context": 0.1, "challenge": 0.15, "solution": 0.5, "results": 0.25}, "opening_style": "problem-solution", "metrics_priority": "technical"}'::JSONB,
    'Deep technical focus with detailed solution architecture. Best for engineering-heavy clients.'
),
(
    'consultative-001',
    'Consultative',
    'consultative',
    '{"emphasis": "business_value", "technical_detail": "medium", "section_weights": {"context": 0.2, "challenge": 0.3, "solution": 0.3, "results": 0.2}, "opening_style": "insight-first", "metrics_priority": "business"}'::JSONB,
    'Business-value driven approach with strategic insights. Best for C-level stakeholders.'
),
(
    'quick-win-001',
    'Quick Win',
    'quick_win',
    '{"emphasis": "speed_results", "technical_detail": "low", "section_weights": {"context": 0.05, "challenge": 0.15, "solution": 0.3, "results": 0.5}, "opening_style": "results-first", "metrics_priority": "time_savings"}'::JSONB,
    'Fast, results-focused approach highlighting quick delivery. Best for urgent projects.'
)
ON CONFLICT (id) DO NOTHING;


-- ============================================================
-- 2. Insert Tone Presets
-- ============================================================

INSERT INTO tone_presets (id, name, tone_type, language_patterns, description)
VALUES
(
    'professional-001',
    'Professional',
    'professional',
    '{"formality": "high", "contractions": false, "sentence_structure": "complex", "vocabulary": "formal", "perspective": "third_person"}'::JSONB,
    'Formal, polished tone suitable for corporate communications.'
),
(
    'conversational-001',
    'Conversational',
    'conversational',
    '{"formality": "medium", "contractions": true, "sentence_structure": "varied", "vocabulary": "accessible", "perspective": "first_person"}'::JSONB,
    'Friendly, approachable tone with natural language flow.'
),
(
    'technical-001',
    'Technical',
    'technical',
    '{"formality": "medium", "contractions": false, "sentence_structure": "precise", "vocabulary": "technical", "perspective": "first_person_plural"}'::JSONB,
    'Technically precise language with industry terminology.'
),
(
    'friendly-001',
    'Friendly',
    'friendly',
    '{"formality": "low", "contractions": true, "sentence_structure": "simple", "vocabulary": "casual", "perspective": "second_person"}'::JSONB,
    'Warm, personable tone that builds rapport quickly.'
)
ON CONFLICT (id) DO NOTHING;


-- ============================================================
-- 3. Verify Seed Data
-- ============================================================

-- Check templates inserted
DO $$
DECLARE
    template_count INT;
BEGIN
    SELECT COUNT(*) INTO template_count FROM proposal_templates;
    RAISE NOTICE 'Inserted % proposal templates', template_count;
END $$;

-- Check tone presets inserted
DO $$
DECLARE
    tone_count INT;
BEGIN
    SELECT COUNT(*) INTO tone_count FROM tone_presets;
    RAISE NOTICE 'Inserted % tone presets', tone_count;
END $$;
