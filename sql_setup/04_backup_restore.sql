-- This file contains commands to backup and restore the database
-- These commands should be run from your command line, not in PostgreSQL

-- BACKUP COMMANDS
-- ------------------------------

-- Backup the entire database (schema and data)
-- pg_dump -U username -W -F c -b -v -f cardealhub_backup.dump cardealhub

-- Backup only the data (no schema)
-- pg_dump -U username -W -F c -b -v -a -f cardealhub_data_backup.dump cardealhub

-- Backup specific tables
-- pg_dump -U username -W -F c -b -v -t table_name -f table_backup.dump cardealhub

-- RESTORE COMMANDS
-- ------------------------------

-- Restore entire database
-- pg_restore -U username -W -d cardealhub cardealhub_backup.dump

-- Restore specific tables
-- pg_restore -U username -W -d cardealhub -t table_name table_backup.dump

-- MAINTENANCE COMMANDS
-- ------------------------------

-- Analyze database for optimization
-- ANALYZE;

-- Vacuum database to reclaim storage and update statistics
-- VACUUM FULL ANALYZE;

-- Reindex all indexes
-- REINDEX DATABASE cardealhub;