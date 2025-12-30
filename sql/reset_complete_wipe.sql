-- ============================================================
-- COMPLETE DATABASE WIPE - NO RECREATION
-- ============================================================
-- ⚠️⚠️⚠️ DESTROYS EVERYTHING - NOTHING GETS RECREATED ⚠️⚠️⚠️
--
-- This drops the entire public schema and recreates it empty.
-- Fastest, cleanest way to wipe everything.
--
-- NO EXTENSIONS
-- NO TABLES
-- NO FUNCTIONS
-- NO VIEWS
-- NO SEQUENCES
-- NO TYPES
-- NOTHING
-- ============================================================

DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;

-- Done. Everything is gone.
