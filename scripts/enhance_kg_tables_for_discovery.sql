-- Enhanced Knowledge Graph Tables for Entity Discovery
-- This script enhances the existing KG tables to support the Entity Discovery workflow

-- Add validation status columns to kg_entities table
ALTER TABLE kg_entities ADD COLUMN validation_status TEXT DEFAULT 'pending';
ALTER TABLE kg_entities ADD COLUMN validation_notes TEXT DEFAULT '';
ALTER TABLE kg_entities ADD COLUMN validated_by TEXT DEFAULT '';
ALTER TABLE kg_entities ADD COLUMN validated_at TIMESTAMP DEFAULT NULL;
ALTER TABLE kg_entities ADD COLUMN extraction_method TEXT DEFAULT 'automated';
ALTER TABLE kg_entities ADD COLUMN extraction_confidence REAL DEFAULT 0.0;

-- Add source metadata to text_entity_mentions
ALTER TABLE text_entity_mentions ADD COLUMN extraction_metadata TEXT DEFAULT '{}';
ALTER TABLE text_entity_mentions ADD COLUMN validation_status TEXT DEFAULT 'pending';

-- Create entity discovery sessions table to track discovery progress
CREATE TABLE IF NOT EXISTS entity_discovery_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    status TEXT DEFAULT 'running',                    -- 'running', 'paused', 'completed', 'error'
    settings TEXT DEFAULT '{}',                       -- JSON: discovery configuration
    progress_data TEXT DEFAULT '{}',                  -- JSON: current progress
    total_slokas INTEGER DEFAULT 0,
    processed_slokas INTEGER DEFAULT 0,
    entities_found INTEGER DEFAULT 0,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create entity conflicts table to track and resolve conflicts
CREATE TABLE IF NOT EXISTS entity_conflicts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conflict_type TEXT NOT NULL,                      -- 'duplicate', 'ambiguous', 'classification'
    description TEXT NOT NULL,
    entity_ids TEXT NOT NULL,                         -- JSON array of conflicting entity IDs
    suggested_resolution TEXT DEFAULT '',
    resolution_action TEXT DEFAULT '',               -- JSON: resolution details
    status TEXT DEFAULT 'pending',                   -- 'pending', 'resolved', 'ignored'
    resolved_by TEXT DEFAULT '',
    resolved_at TIMESTAMP DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create entity validation queue table for organized validation workflow
CREATE TABLE IF NOT EXISTS entity_validation_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id TEXT NOT NULL,
    priority INTEGER DEFAULT 5,                      -- 1 (high) to 10 (low)
    assigned_to TEXT DEFAULT '',
    status TEXT DEFAULT 'pending',                   -- 'pending', 'in_review', 'completed', 'skipped'
    notes TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (entity_id) REFERENCES kg_entities(kg_id)
);

-- Create discovery metrics table for analytics
CREATE TABLE IF NOT EXISTS discovery_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    metric_type TEXT NOT NULL,                       -- 'processing_rate', 'confidence_dist', 'entity_types'
    metric_data TEXT NOT NULL,                       -- JSON data
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES entity_discovery_sessions(session_id)
);

-- Enhanced indexes for Entity Discovery
CREATE INDEX IF NOT EXISTS idx_kg_entities_validation_status ON kg_entities(validation_status);
CREATE INDEX IF NOT EXISTS idx_kg_entities_extraction_method ON kg_entities(extraction_method);
CREATE INDEX IF NOT EXISTS idx_kg_entities_confidence ON kg_entities(extraction_confidence);
CREATE INDEX IF NOT EXISTS idx_text_mentions_validation_status ON text_entity_mentions(validation_status);
CREATE INDEX IF NOT EXISTS idx_discovery_sessions_status ON entity_discovery_sessions(status);
CREATE INDEX IF NOT EXISTS idx_entity_conflicts_status ON entity_conflicts(status);
CREATE INDEX IF NOT EXISTS idx_validation_queue_status ON entity_validation_queue(status);
CREATE INDEX IF NOT EXISTS idx_validation_queue_priority ON entity_validation_queue(priority);
CREATE INDEX IF NOT EXISTS idx_discovery_metrics_session ON discovery_metrics(session_id);
CREATE INDEX IF NOT EXISTS idx_discovery_metrics_type ON discovery_metrics(metric_type);

-- Update existing entities to have validation status if they don't already
UPDATE kg_entities 
SET validation_status = 'validated', 
    extraction_method = 'manual',
    extraction_confidence = 1.0,
    validated_at = CURRENT_TIMESTAMP
WHERE validation_status IS NULL OR validation_status = '';

-- Update existing mentions to have validation status
UPDATE text_entity_mentions 
SET validation_status = 'validated'
WHERE validation_status IS NULL OR validation_status = '';

-- Create view for discovery dashboard
CREATE VIEW IF NOT EXISTS discovery_dashboard_view AS
SELECT 
    e.entity_type,
    e.validation_status,
    e.extraction_method,
    COUNT(*) as entity_count,
    AVG(e.extraction_confidence) as avg_confidence,
    COUNT(tem.id) as total_mentions
FROM kg_entities e
LEFT JOIN text_entity_mentions tem ON e.kg_id = tem.entity_id
GROUP BY e.entity_type, e.validation_status, e.extraction_method;

-- Create view for pending validation
CREATE VIEW IF NOT EXISTS pending_validation_view AS
SELECT 
    e.*,
    COUNT(tem.id) as mention_count,
    MAX(tem.confidence) as max_mention_confidence,
    MIN(tem.confidence) as min_mention_confidence
FROM kg_entities e
LEFT JOIN text_entity_mentions tem ON e.kg_id = tem.entity_id
WHERE e.validation_status = 'pending'
GROUP BY e.kg_id
ORDER BY mention_count DESC, e.extraction_confidence DESC;