-- Knowledge Graph Tables for Ramayana Database
-- This script adds KG tables to the existing ramayanam.db SQLite database

-- Knowledge Graph entities
CREATE TABLE IF NOT EXISTS kg_entities (
    kg_id TEXT PRIMARY KEY,                    -- URI like http://example.org/entity/rama
    entity_type TEXT NOT NULL,                 -- Person, Place, Event, Object, Concept
    labels TEXT NOT NULL,                      -- JSON: {"en": "Rama", "sa": "राम"}
    properties TEXT DEFAULT '{}',              -- JSON: {"epithets": ["राघव"], "confidence": 0.95}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Knowledge Graph relationships
CREATE TABLE IF NOT EXISTS kg_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id TEXT NOT NULL,                  -- Subject entity kg_id
    predicate TEXT NOT NULL,                   -- Relationship type (hasSpouse, devoteeOf, etc.)
    object_id TEXT NOT NULL,                   -- Object entity kg_id
    metadata TEXT DEFAULT '{}',                -- JSON: {"confidence": 0.9, "source": "1.1.8"}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES kg_entities(kg_id),
    FOREIGN KEY (object_id) REFERENCES kg_entities(kg_id)
);

-- Entity mentions in text units (connects KG to existing slokas)
CREATE TABLE IF NOT EXISTS text_entity_mentions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text_unit_id TEXT NOT NULL,               -- Sloka ID like "1.1.8"
    entity_id TEXT NOT NULL,                  -- Entity kg_id
    span_start INTEGER NOT NULL,              -- Start position in text
    span_end INTEGER NOT NULL,                -- End position in text
    confidence REAL DEFAULT 1.0,              -- Confidence score 0.0-1.0
    source_type TEXT DEFAULT 'automated',     -- 'automated', 'manual', 'verified'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (entity_id) REFERENCES kg_entities(kg_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_kg_entities_type ON kg_entities(entity_type);
CREATE INDEX IF NOT EXISTS idx_kg_relationships_subject ON kg_relationships(subject_id);
CREATE INDEX IF NOT EXISTS idx_kg_relationships_predicate ON kg_relationships(predicate);
CREATE INDEX IF NOT EXISTS idx_kg_relationships_object ON kg_relationships(object_id);
CREATE INDEX IF NOT EXISTS idx_text_mentions_unit ON text_entity_mentions(text_unit_id);
CREATE INDEX IF NOT EXISTS idx_text_mentions_entity ON text_entity_mentions(entity_id);
CREATE INDEX IF NOT EXISTS idx_text_mentions_confidence ON text_entity_mentions(confidence);

-- Sample data insertion (will be replaced by automated extraction)
INSERT OR IGNORE INTO kg_entities (kg_id, entity_type, labels, properties) VALUES
('http://ramayanam.hanuma.com/entity/rama', 'Person', '{"en": "Rama", "sa": "राम"}', '{"epithets": ["राघव", "दाशरथि"], "confidence": 0.95}'),
('http://ramayanam.hanuma.com/entity/sita', 'Person', '{"en": "Sita", "sa": "सीता"}', '{"epithets": ["मैथिली", "वैदेही"], "confidence": 0.95}'),
('http://ramayanam.hanuma.com/entity/hanuman', 'Person', '{"en": "Hanuman", "sa": "हनुमान्"}', '{"epithets": ["पवनात्मज", "मारुति"], "confidence": 0.95}'),
('http://ramayanam.hanuma.com/entity/ayodhya', 'Place', '{"en": "Ayodhya", "sa": "अयोध्या"}', '{"type": "city", "confidence": 0.95}'),
('http://ramayanam.hanuma.com/entity/dharma', 'Concept', '{"en": "Dharma", "sa": "धर्म"}', '{"category": "philosophy", "confidence": 0.90}');

-- Sample relationships
INSERT OR IGNORE INTO kg_relationships (subject_id, predicate, object_id, metadata) VALUES
('http://ramayanam.hanuma.com/entity/rama', 'hasSpouse', 'http://ramayanam.hanuma.com/entity/sita', '{"confidence": 0.99}'),
('http://ramayanam.hanuma.com/entity/hanuman', 'devoteeOf', 'http://ramayanam.hanuma.com/entity/rama', '{"confidence": 0.99}'),
('http://ramayanam.hanuma.com/entity/rama', 'rules', 'http://ramayanam.hanuma.com/entity/ayodhya', '{"confidence": 0.95}'),
('http://ramayanam.hanuma.com/entity/rama', 'embodies', 'http://ramayanam.hanuma.com/entity/dharma', '{"confidence": 0.90}');