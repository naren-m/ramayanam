# Ramayana Knowledge Graph: Implementation Summary & Architecture

## Executive Summary

This document summarizes the completed knowledge graph implementation for the Ramayana digital corpus platform. The system successfully transforms the existing text-based platform into a semantic knowledge platform with automated entity extraction, relationship mapping, and API-driven access to structured knowledge.

## ✅ Implementation Status: COMPLETED

**Phase 1 Foundation**: ✅ Complete  
**Core Features**: ✅ Automated extraction, API endpoints, Docker deployment  
**Entity Coverage**: ✅ 10 core entities, 25,319 text mentions  
**URI Schema**: ✅ Updated to `ramayanam.hanuma.com` domain

## Architectural Decisions Summary

### 1. **Automated vs Manual Entity Creation**

**Decision**: Chose automated entity extraction over manual creation  
**Rationale**: 
- Scalable and repeatable approach for large corpus
- Reduces human error and bias in entity identification
- Consistent pattern-based recognition across Sanskrit and English text
- Can process entire Ramayana corpus (2+ million words) efficiently

**Implementation**: `RamayanaEntityExtractor` class with regex patterns for entity recognition

### 2. **Database Integration Strategy**

**Decision**: Hybrid approach using existing SQLite database + new KG tables  
**Rationale**:
- Preserves existing data and infrastructure
- Minimal disruption to current system
- Future-ready for vector database integration
- Maintains ACID properties for relationships

**Schema**: Three new tables: `kg_entities`, `kg_relationships`, `text_entity_mentions`

### 3. **URI Schema Design**

**Decision**: Semantic URIs using `http://ramayanam.hanuma.com/entity/{id}` format  
**Rationale**:
- Follows Linked Data best practices
- Domain reflects actual project ownership
- Consistent namespace for all entities
- Supports future federation with other knowledge graphs

### 4. **Entity Type Taxonomy**

**Decision**: Five core entity types: Person, Place, Event, Object, Concept  
**Rationale**:
- Covers all major semantic categories in Ramayana
- Simple enough for initial implementation
- Extensible for future refinement
- Aligned with common ontology patterns

### 5. **Relationship Modeling**

**Decision**: RDF-style subject-predicate-object triples with metadata  
**Rationale**:
- Standard knowledge graph representation
- Supports complex relationship semantics
- Metadata allows confidence scores and provenance
- Compatible with future SPARQL querying

### 6. **Multi-language Support**

**Decision**: JSON-based label storage with language codes  
**Rationale**:
- Supports Sanskrit (Devanagari) and English labels
- Flexible for adding more languages
- Efficient storage in JSONB columns
- Follows internationalization standards

### 7. **API Design Pattern**

**Decision**: RESTful API with JSON responses, separate KG blueprint  
**Rationale**:
- Consistent with existing API architecture
- Clear separation of concerns
- Easy to test and document
- Supports future GraphQL migration

### 8. **Deployment Strategy**

**Decision**: Docker containerization with backend-only approach  
**Rationale**:
- Isolated development environment
- Easier dependency management
- Supports CI/CD pipelines
- Simplified deployment to production

### 9. **Text Annotation Approach**

**Decision**: Span-based entity mentions with confidence scores  
**Rationale**:
- Precise location tracking for entity occurrences
- Supports highlighting in UI
- Confidence scores enable quality filtering
- Compatible with NLP annotation standards

### 10. **Data Processing Pipeline**

**Decision**: Batch processing with hierarchical text traversal  
**Rationale**:
- Processes entire corpus systematically
- Respects existing file structure (Kanda→Sarga→Sloka)
- Allows for incremental updates
- Maintains data lineage and provenance

## Current Architecture Overview

### ✅ **Implemented Components**

1. **Knowledge Graph Models** (`api/models/kg_models.py`)
   - `KGEntity`, `KGRelationship`, `SemanticAnnotation` classes
   - EntityType enum with five core types
   - JSON serialization support

2. **Automated Extraction Pipeline** (`api/services/automated_entity_extraction.py`)
   - Pattern-based entity recognition
   - Corpus-wide processing capabilities
   - Confidence scoring and validation

3. **Database Service** (`api/services/kg_database_service.py`)
   - CRUD operations for entities and relationships
   - Search and statistics functionality
   - Transaction management

4. **REST API Endpoints** (`api/controllers/kg_controller.py`)
   - `/api/kg/entities` - Entity listing and filtering
   - `/api/kg/search` - Entity search functionality
   - `/api/kg/statistics` - Knowledge graph metrics
   - `/api/kg/extract` - Automated extraction trigger

5. **Database Schema** (`scripts/add_kg_tables.sql`)
   - Three tables with proper indexing
   - Foreign key constraints
   - Performance optimization

6. **Docker Deployment** (`docker-compose.backend.yml`, `Dockerfile.backend`)
   - Containerized backend service
   - Health checks and volume mounts
   - Port mapping and environment configuration

### ✅ **Current Knowledge Graph Statistics**

- **Total Entities**: 10 core entities extracted
- **Entity Types**: Person (5), Place (3), Concept (2)  
- **Text Mentions**: 25,319 annotated spans
- **Coverage**: Major characters, places, and concepts
- **Languages**: Sanskrit and English labels
- **URI Format**: `http://ramayanam.hanuma.com/entity/{id}`

### ✅ **API Functionality**

All endpoints operational at `http://localhost:8080/api/kg/`:
- Entity retrieval with relationship data
- Search by name/label across languages
- Statistics and analytics
- Automated extraction triggering

## Future Development Roadmap

The current implementation provides a solid foundation for advanced knowledge graph features. Below are the planned phases for continued development:

## Phase 2: Enhanced Relationships & Semantic Search (Future)

**Goals**: 
- Add relationship extraction between entities
- Implement vector-based semantic search
- Create graph visualization components

**Key Features**:
- Automated relationship detection (family, devotion, conflict relationships)
- Vector embeddings for semantic similarity search
- Interactive entity relationship graphs
- Enhanced UI with knowledge graph integration

## Phase 3: AI Integration & RAG Enhancement (Future)

**Goals**:
- Integrate knowledge graph with AI chat system
- Provide entity-aware contextual responses
- Generate citations with knowledge graph links

**Key Features**:
- Knowledge graph-enhanced RAG (Retrieval Augmented Generation)
- Entity-aware conversation memory
- Automatic citation generation with entity links
- Context-rich AI responses using relationship data

## Phase 4: Multi-Text Expansion (Future)

**Goals**:
- Extend to other sacred texts (Bhagavad Gita, Mahabharata)
- Enable cross-text entity resolution and comparison
- Build universal sacred text knowledge platform

**Key Features**:
- Cross-text entity mapping and resolution
- Comparative analysis tools
- Universal entity browser
- Federated knowledge graph queries

---

## Legacy Implementation Plan (Original Detailed Design)

The following sections contain the original comprehensive implementation plan that guided the current development. This serves as reference for future phases:

### 1.1 JSON-LD Schema Implementation

Create comprehensive ontology schema for Ramayana entities and relationships:

```json
{
  "@context": {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "schema": "http://schema.org/",
    "ramayana": "http://example.org/ramayana/ontology/"
  },
  "@graph": [
    {
      "@id": "rama:Person",
      "@type": "rdfs:Class",
      "rdfs:label": "Person",
      "rdfs:comment": "A lead character in the Ramayana epic"
    },
    {
      "@id": "rama:hasSpouse",
      "@type": "rdf:Property",
      "rdfs:domain": "rama:Person",
      "rdfs:range": "rama:Person",
      "rdfs:label": "has spouse"
    }
  ]
}
```

### 1.2 Knowledge Graph Models

Add new models to extend existing architecture:

```python
# api/models/kg_models.py
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

class EntityType(Enum):
    PERSON = "Person"
    PLACE = "Place"
    EVENT = "Event"
    OBJECT = "Object"
    CONCEPT = "Concept"

@dataclass
class KGEntity:
    """Knowledge Graph Entity"""
    kg_id: str  # http://example.org/entity/Rama
    entity_type: EntityType
    labels: Dict[str, str]  # {"en": "Rama", "sa": "राम"}
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}

@dataclass
class KGRelationship:
    """Knowledge Graph Relationship"""
    subject_id: str
    predicate: str
    object_id: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class SemanticAnnotation:
    """Entity mention in text"""
    text_unit_id: str
    entity_id: str
    span_start: int
    span_end: int
    confidence: float = 1.0
```

### 1.3 Enhanced Text Models

Extend existing `TextUnit` class with semantic capabilities:

```python
# api/models/text_models.py (additions)
class EnhancedTextUnit(TextUnit):
    """TextUnit with semantic annotations"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.semantic_annotations: List[SemanticAnnotation] = []
        self.mentioned_entities: List[str] = []
        self.concepts: List[str] = []
        
    def add_entity_mention(self, entity_id: str, span: Tuple[int, int], confidence: float = 1.0):
        """Add entity mention annotation"""
        annotation = SemanticAnnotation(
            text_unit_id=self.id,
            entity_id=entity_id,
            span_start=span[0],
            span_end=span[1],
            confidence=confidence
        )
        self.semantic_annotations.append(annotation)
        if entity_id not in self.mentioned_entities:
            self.mentioned_entities.append(entity_id)
    
    def get_entity_context(self) -> Dict[str, Any]:
        """Get semantic context for this text unit"""
        return {
            "entities": self.mentioned_entities,
            "concepts": self.concepts,
            "annotations": [
                {
                    "entity_id": ann.entity_id,
                    "span": [ann.span_start, ann.span_end],
                    "confidence": ann.confidence
                } for ann in self.semantic_annotations
            ]
        }
```

### 1.4 Database Schema Extension

Add knowledge graph tables to existing PostgreSQL schema:

```sql
-- Knowledge Graph entities
CREATE TABLE kg_entities (
    kg_id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL,
    labels JSONB NOT NULL,
    properties JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Knowledge Graph relationships
CREATE TABLE kg_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject_id TEXT REFERENCES kg_entities(kg_id),
    predicate TEXT NOT NULL,
    object_id TEXT REFERENCES kg_entities(kg_id),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Entity mentions in text units
CREATE TABLE text_entity_mentions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    text_unit_id TEXT NOT NULL,
    entity_id TEXT REFERENCES kg_entities(kg_id),
    span_start INTEGER NOT NULL,
    span_end INTEGER NOT NULL,
    confidence FLOAT DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_kg_entities_type ON kg_entities(entity_type);
CREATE INDEX idx_kg_relationships_subject ON kg_relationships(subject_id);
CREATE INDEX idx_kg_relationships_predicate ON kg_relationships(predicate);
CREATE INDEX idx_text_mentions_unit ON text_entity_mentions(text_unit_id);
CREATE INDEX idx_text_mentions_entity ON text_entity_mentions(entity_id);
```

**Phase 1 Deliverables**:

- JSON-LD schema with 50+ core entities
- Enhanced data models with KG integration
- Database schema supporting semantic data
- Initial Ramayana entities (Rama, Sita, Hanuman, Ravana, Dasharatha)

## Phase 2: Integration (Months 3-4)

**Goal**: Integrate knowledge graph with existing text processing

### 2.1 Knowledge Graph Service

Create comprehensive KG management service:

```python
# api/services/kg_service.py
from typing import List, Dict, Optional, Any
from api.models.kg_models import KGEntity, KGRelationship, EntityType
from api.models.text_models import TextUnit

class KnowledgeGraphService:
    """Service for managing knowledge graph operations"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.logger = logging.getLogger(__name__)
    
    def create_entity(self, entity: KGEntity) -> KGEntity:
        """Create new KG entity"""
        query = """
        INSERT INTO kg_entities (kg_id, entity_type, labels, properties)
        VALUES (%s, %s, %s, %s)
        RETURNING *
        """
        # Execute query and return entity
        
    def get_entity(self, kg_id: str) -> Optional[KGEntity]:
        """Get entity by ID"""
        query = "SELECT * FROM kg_entities WHERE kg_id = %s"
        # Execute and return entity
        
    def create_relationship(self, relationship: KGRelationship) -> KGRelationship:
        """Create relationship between entities"""
        query = """
        INSERT INTO kg_relationships (subject_id, predicate, object_id, metadata)
        VALUES (%s, %s, %s, %s)
        RETURNING *
        """
        # Execute query
        
    def get_entity_relationships(self, kg_id: str) -> List[KGRelationship]:
        """Get all relationships for an entity"""
        query = """
        SELECT * FROM kg_relationships 
        WHERE subject_id = %s OR object_id = %s
        """
        # Execute and return relationships
        
    def annotate_text_unit(self, text_unit: TextUnit, entities: List[str]):
        """Add entity annotations to text unit"""
        # Entity recognition and annotation logic
        
    def get_context_for_text_unit(self, text_unit_id: str) -> Dict[str, Any]:
        """Get semantic context for a text unit"""
        query = """
        SELECT e.*, tem.span_start, tem.span_end, tem.confidence
        FROM text_entity_mentions tem
        JOIN kg_entities e ON tem.entity_id = e.kg_id
        WHERE tem.text_unit_id = %s
        """
        # Execute and build context
```

### 2.2 Entity Extraction Pipeline

Implement automated entity recognition:

```python
# api/services/entity_extraction.py
import re
from typing import List, Tuple, Dict
from api.models.kg_models import EntityType

class EntityExtractor:
    """Extract entities from Sanskrit and English text"""
    
    def __init__(self):
        # Predefined entity patterns
        self.character_patterns = {
            'rama': ['राम', 'Rama', 'Rāma'],
            'sita': ['सीता', 'Sita', 'Sītā'],
            'hanuman': ['हनुमान्', 'Hanuman', 'Hanumān'],
            'ravana': ['रावण', 'Ravana', 'Rāvaṇa']
        }
        
        self.place_patterns = {
            'ayodhya': ['अयोध्या', 'Ayodhya', 'Ayodhyā'],
            'lanka': ['लंका', 'Lanka', 'Laṅkā'],
            'kishkindha': ['किष्किन्धा', 'Kishkindha', 'Kiṣkindhā']
        }
    
    def extract_entities(self, text: str) -> List[Tuple[str, int, int, EntityType]]:
        """Extract entities from text with positions"""
        entities = []
        
        # Extract characters
        for entity_id, patterns in self.character_patterns.items():
            entities.extend(self._find_patterns(text, entity_id, patterns, EntityType.PERSON))
        
        # Extract places
        for entity_id, patterns in self.place_patterns.items():
            entities.extend(self._find_patterns(text, entity_id, patterns, EntityType.PLACE))
        
        return entities
    
    def _find_patterns(self, text: str, entity_id: str, patterns: List[str], entity_type: EntityType) -> List[Tuple[str, int, int, EntityType]]:
        """Find pattern matches in text"""
        matches = []
        for pattern in patterns:
            for match in re.finditer(re.escape(pattern), text, re.IGNORECASE):
                matches.append((entity_id, match.start(), match.end(), entity_type))
        return matches
```

### 2.3 API Enhancements

Add knowledge graph endpoints:

```python
# api/controllers/kg_controller.py
from flask import Blueprint, request, jsonify
from api.services.kg_service import KnowledgeGraphService

kg_blueprint = Blueprint('kg', __name__)

@kg_blueprint.route('/entities', methods=['GET'])
def get_entities():
    """Get all entities with optional filtering"""
    entity_type = request.args.get('type')
    limit = int(request.args.get('limit', 50))
    
    # Get entities from service
    entities = kg_service.get_entities(entity_type=entity_type, limit=limit)
    
    return jsonify({
        'entities': [entity.serialize() for entity in entities],
        'total': len(entities)
    })

@kg_blueprint.route('/entities/<entity_id>', methods=['GET'])
def get_entity(entity_id: str):
    """Get specific entity with relationships"""
    entity = kg_service.get_entity(entity_id)
    if not entity:
        return jsonify({'error': 'Entity not found'}), 404
    
    relationships = kg_service.get_entity_relationships(entity_id)
    
    return jsonify({
        'entity': entity.serialize(),
        'relationships': [rel.serialize() for rel in relationships]
    })

@kg_blueprint.route('/search', methods=['POST'])
def semantic_search():
    """Semantic search across entities and text"""
    data = request.get_json()
    query = data.get('query', '')
    
    # Perform semantic search
    results = kg_service.semantic_search(query)
    
    return jsonify({
        'results': results,
        'query': query
    })
```

**Phase 2 Deliverables**:

- Complete KG service implementation
- Entity extraction pipeline
- Enhanced API with KG endpoints
- 100+ entities with relationships

## Phase 3: Semantic Search (Months 5-6)

**Goal**: Implement advanced semantic search capabilities

### 3.1 Vector Database Integration

Set up semantic search infrastructure:

```python
# api/services/vector_service.py
import weaviate
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any

class VectorService:
    """Service for semantic search using vector embeddings"""
    
    def __init__(self, weaviate_url: str):
        self.client = weaviate.Client(weaviate_url)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.setup_schema()
    
    def setup_schema(self):
        """Set up Weaviate schema for text units"""
        schema = {
            "classes": [
                {
                    "class": "TextUnit",
                    "properties": [
                        {"name": "unitId", "dataType": ["string"]},
                        {"name": "originalText", "dataType": ["text"]},
                        {"name": "translation", "dataType": ["text"]},
                        {"name": "hierarchy", "dataType": ["object"]},
                        {"name": "entities", "dataType": ["string[]"]},
                        {"name": "concepts", "dataType": ["string[]"]}
                    ]
                }
            ]
        }
        self.client.schema.create(schema)
    
    def index_text_unit(self, text_unit: TextUnit):
        """Index a text unit with embeddings"""
        # Combine text for embedding
        combined_text = f"{text_unit.original_text} {text_unit.get_primary_translation()}"
        
        # Generate embedding
        vector = self.model.encode(combined_text)
        
        # Store in Weaviate
        self.client.data_object.create(
            data_object={
                "unitId": text_unit.id,
                "originalText": text_unit.original_text,
                "translation": text_unit.get_primary_translation(),
                "hierarchy": text_unit.hierarchy,
                "entities": text_unit.mentioned_entities,
                "concepts": text_unit.concepts
            },
            class_name="TextUnit",
            vector=vector.tolist()
        )
    
    def semantic_search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Perform semantic search"""
        query_vector = self.model.encode(query)
        
        result = self.client.query.get("TextUnit", [
            "unitId", "originalText", "translation", "hierarchy", "entities", "concepts"
        ]).with_near_vector({
            "vector": query_vector.tolist()
        }).with_limit(limit).do()
        
        return result.get("data", {}).get("Get", {}).get("TextUnit", [])
```

### 3.2 Enhanced Search Service

Create unified search interface:

```python
# api/services/enhanced_search_service.py
from typing import List, Dict, Any, Optional
from api.services.vector_service import VectorService
from api.services.kg_service import KnowledgeGraphService
from api.services.fuzzy_search_service import FuzzySearchService

class EnhancedSearchService:
    """Unified search service combining text, semantic, and graph search"""
    
    def __init__(self, vector_service: VectorService, kg_service: KnowledgeGraphService, fuzzy_service: FuzzySearchService):
        self.vector_service = vector_service
        self.kg_service = kg_service
        self.fuzzy_service = fuzzy_service
    
    def unified_search(self, query: str, search_type: str = "hybrid", limit: int = 10) -> Dict[str, Any]:
        """Perform unified search across all modalities"""
        results = {}
        
        if search_type in ["hybrid", "semantic"]:
            # Semantic search
            semantic_results = self.vector_service.semantic_search(query, limit)
            results["semantic"] = semantic_results
        
        if search_type in ["hybrid", "text"]:
            # Text search
            text_results = self.fuzzy_service.search(query, limit)
            results["text"] = text_results
        
        if search_type in ["hybrid", "entity"]:
            # Entity-based search
            entity_results = self.kg_service.search_by_entity(query, limit)
            results["entities"] = entity_results
        
        # Combine and rank results
        if search_type == "hybrid":
            combined_results = self._combine_results(results)
            return {"results": combined_results, "components": results}
        
        return results
    
    def _combine_results(self, results: Dict[str, List]) -> List[Dict[str, Any]]:
        """Combine results from different search methods"""
        # Implement result fusion logic
        combined = []
        
        # Add semantic results with high weight
        for result in results.get("semantic", []):
            combined.append({
                **result,
                "search_type": "semantic",
                "score": result.get("_additional", {}).get("distance", 0)
            })
        
        # Add text results
        for result in results.get("text", []):
            combined.append({
                **result,
                "search_type": "text",
                "score": result.get("score", 0)
            })
        
        # Sort by relevance
        combined.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        return combined[:10]  # Return top 10
```

**Phase 3 Deliverables**:

- Vector database with semantic embeddings
- Unified search service
- Enhanced search API endpoints
- Semantic search UI components

## Phase 4: AI Integration (Months 7-8)

**Goal**: Enhance AI chat with knowledge graph context

### 4.1 Knowledge Graph RAG Service

Create advanced RAG with KG context:

```python
# api/services/kg_rag_service.py
from typing import List, Dict, Any
from api.services.kg_service import KnowledgeGraphService
from api.services.vector_service import VectorService
from api.services.chat_service import ChatService

class KnowledgeGraphRAGService:
    """RAG service enhanced with knowledge graph context"""
    
    def __init__(self, kg_service: KnowledgeGraphService, vector_service: VectorService, chat_service: ChatService):
        self.kg_service = kg_service
        self.vector_service = vector_service
        self.chat_service = chat_service
    
    def generate_response(self, query: str, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate AI response with KG context"""
        
        # 1. Extract entities from query
        entities_in_query = self._extract_query_entities(query)
        
        # 2. Semantic search for relevant passages
        relevant_passages = self.vector_service.semantic_search(query, limit=5)
        
        # 3. Get KG context for passages and entities
        kg_context = self._build_kg_context(relevant_passages, entities_in_query)
        
        # 4. Build grounded prompt
        prompt = self._build_grounded_prompt(query, relevant_passages, kg_context)
        
        # 5. Generate response
        response = self.chat_service.generate_response(prompt, conversation_history)
        
        # 6. Add citations and context
        return {
            'response': response,
            'sources': relevant_passages,
            'entities': kg_context.get('entities', []),
            'relationships': kg_context.get('relationships', []),
            'concepts': kg_context.get('concepts', [])
        }
    
    def _extract_query_entities(self, query: str) -> List[str]:
        """Extract entities from user query"""
        # Use entity extraction to find mentioned entities
        return self.kg_service.extract_entities_from_text(query)
    
    def _build_kg_context(self, passages: List[Dict], query_entities: List[str]) -> Dict[str, Any]:
        """Build comprehensive KG context"""
        context = {
            'entities': {},
            'relationships': [],
            'concepts': set()
        }
        
        # Get entities from passages
        for passage in passages:
            unit_id = passage.get('unitId')
            if unit_id:
                unit_context = self.kg_service.get_context_for_text_unit(unit_id)
                
                # Add entities
                for entity_id in unit_context.get('entities', []):
                    if entity_id not in context['entities']:
                        entity = self.kg_service.get_entity(entity_id)
                        context['entities'][entity_id] = entity
                
                # Add relationships
                for entity_id in unit_context.get('entities', []):
                    relationships = self.kg_service.get_entity_relationships(entity_id)
                    context['relationships'].extend(relationships)
                
                # Add concepts
                context['concepts'].update(unit_context.get('concepts', []))
        
        # Add query entities
        for entity_id in query_entities:
            if entity_id not in context['entities']:
                entity = self.kg_service.get_entity(entity_id)
                context['entities'][entity_id] = entity
        
        return context
    
    def _build_grounded_prompt(self, query: str, passages: List[Dict], kg_context: Dict[str, Any]) -> str:
        """Build grounded prompt with KG context"""
        prompt_parts = []
        
        # System prompt
        prompt_parts.append("""You are a helpful assistant specializing in Hindu sacred texts, particularly the Ramayana. 
        Answer questions using only the provided text passages and knowledge graph context. 
        Always cite your sources using the format [Text Unit ID].""")
        
        # Add KG context
        if kg_context.get('entities'):
            prompt_parts.append("\n**Entities mentioned:**")
            for entity_id, entity in kg_context['entities'].items():
                prompt_parts.append(f"- {entity.labels.get('en', entity_id)}: {entity.entity_type}")
        
        if kg_context.get('relationships'):
            prompt_parts.append("\n**Key relationships:**")
            for rel in kg_context['relationships'][:5]:  # Limit to top 5
                prompt_parts.append(f"- {rel.subject_id} {rel.predicate} {rel.object_id}")
        
        # Add passages
        prompt_parts.append("\n**Relevant text passages:**")
        for i, passage in enumerate(passages, 1):
            prompt_parts.append(f"{i}. [{passage.get('unitId', 'Unknown')}] {passage.get('originalText', '')}")
            if passage.get('translation'):
                prompt_parts.append(f"   Translation: {passage.get('translation')}")
        
        # Add user query
        prompt_parts.append(f"\n**User Question:** {query}")
        
        return "\n".join(prompt_parts)
```

### 4.2 Enhanced Chat Controller

Update chat interface with KG capabilities:

```python
# api/controllers/chat_controller.py (enhanced)
@chat_blueprint.route('/chat', methods=['POST'])
def chat_with_kg():
    """Chat endpoint with knowledge graph enhancement"""
    data = request.get_json()
    message = data.get('message', '')
    conversation_id = data.get('conversation_id')
    
    # Get or create conversation
    conversation = chat_service.get_or_create_conversation(conversation_id)
    
    # Generate response with KG context
    response_data = kg_rag_service.generate_response(message, conversation.history)
    
    # Save to conversation
    chat_service.add_message(conversation_id, 'user', message)
    chat_service.add_message(conversation_id, 'assistant', response_data['response'])
    
    return jsonify({
        'response': response_data['response'],
        'sources': response_data['sources'],
        'entities': response_data['entities'],
        'relationships': response_data['relationships'],
        'conversation_id': conversation_id
    })
```

**Phase 4 Deliverables**:

- KG-enhanced RAG service
- Intelligent chat with entity context
- Citation generation with KG links
- Multi-turn conversations with memory

## Phase 5: Visualization & Analytics (Months 9-10)

**Goal**: Add graph visualization and analytical capabilities

### 5.1 Graph Visualization API

Create endpoints for graph visualization:

```python
# api/controllers/visualization_controller.py
from flask import Blueprint, request, jsonify
from api.services.kg_service import KnowledgeGraphService

viz_blueprint = Blueprint('visualization', __name__)

@viz_blueprint.route('/entity-graph/<entity_id>', methods=['GET'])
def get_entity_graph(entity_id: str):
    """Get graph data for entity visualization"""
    depth = int(request.args.get('depth', 2))
    
    # Get entity and its neighborhood
    entity = kg_service.get_entity(entity_id)
    relationships = kg_service.get_entity_relationships(entity_id)
    
    # Build graph data
    nodes = [{'id': entity.kg_id, 'label': entity.labels.get('en', entity.kg_id), 'type': entity.entity_type}]
    edges = []
    
    for rel in relationships:
        # Add connected entities
        if rel.subject_id != entity_id:
            connected_entity = kg_service.get_entity(rel.subject_id)
            nodes.append({
                'id': connected_entity.kg_id,
                'label': connected_entity.labels.get('en', connected_entity.kg_id),
                'type': connected_entity.entity_type
            })
        
        if rel.object_id != entity_id:
            connected_entity = kg_service.get_entity(rel.object_id)
            nodes.append({
                'id': connected_entity.kg_id,
                'label': connected_entity.labels.get('en', connected_entity.kg_id),
                'type': connected_entity.entity_type
            })
        
        edges.append({
            'source': rel.subject_id,
            'target': rel.object_id,
            'label': rel.predicate,
            'type': rel.predicate
        })
    
    return jsonify({
        'nodes': nodes,
        'edges': edges,
        'center': entity_id
    })

@viz_blueprint.route('/concept-map', methods=['GET'])
def get_concept_map():
    """Get concept relationship map"""
    concepts = kg_service.get_entities_by_type('Concept')
    
    # Build concept network
    nodes = []
    edges = []
    
    for concept in concepts:
        nodes.append({
            'id': concept.kg_id,
            'label': concept.labels.get('en', concept.kg_id),
            'type': 'concept'
        })
        
        # Get related concepts
        relationships = kg_service.get_entity_relationships(concept.kg_id)
        for rel in relationships:
            if rel.predicate in ['relatedTo', 'partOf', 'exemplifies']:
                edges.append({
                    'source': rel.subject_id,
                    'target': rel.object_id,
                    'label': rel.predicate
                })
    
    return jsonify({
        'nodes': nodes,
        'edges': edges
    })
```

### 5.2 Frontend Visualization Components

Create React components for graph visualization:

```typescript
// ui/src/components/KnowledgeGraph/EntityGraph.tsx
import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';

interface Node {
  id: string;
  label: string;
  type: string;
}

interface Edge {
  source: string;
  target: string;
  label: string;
  type: string;
}

interface EntityGraphProps {
  entityId: string;
  depth?: number;
}

export const EntityGraph: React.FC<EntityGraphProps> = ({ entityId, depth = 2 }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [graphData, setGraphData] = useState<{ nodes: Node[]; edges: Edge[] } | null>(null);
  
  useEffect(() => {
    fetchGraphData();
  }, [entityId, depth]);
  
  const fetchGraphData = async () => {
    try {
      const response = await fetch(`/api/visualization/entity-graph/${entityId}?depth=${depth}`);
      const data = await response.json();
      setGraphData(data);
    } catch (error) {
      console.error('Failed to fetch graph data:', error);
    }
  };
  
  useEffect(() => {
    if (!graphData || !svgRef.current) return;
    
    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove(); // Clear previous content
    
    const width = 800;
    const height = 600;
    
    // Create force simulation
    const simulation = d3.forceSimulation(graphData.nodes)
      .force('link', d3.forceLink(graphData.edges).id((d: any) => d.id))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2));
    
    // Create links
    const link = svg.append('g')
      .selectAll('line')
      .data(graphData.edges)
      .enter().append('line')
      .attr('stroke', '#999')
      .attr('stroke-width', 2);
    
    // Create nodes
    const node = svg.append('g')
      .selectAll('circle')
      .data(graphData.nodes)
      .enter().append('circle')
      .attr('r', 8)
      .attr('fill', (d: Node) => getNodeColor(d.type))
      .call(d3.drag<SVGCircleElement, Node>()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended));
    
    // Add labels
    const label = svg.append('g')
      .selectAll('text')
      .data(graphData.nodes)
      .enter().append('text')
      .text((d: Node) => d.label)
      .attr('font-size', 12)
      .attr('dx', 15)
      .attr('dy', 4);
    
    // Update positions on tick
    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);
      
      node
        .attr('cx', (d: any) => d.x)
        .attr('cy', (d: any) => d.y);
      
      label
        .attr('x', (d: any) => d.x)
        .attr('y', (d: any) => d.y);
    });
    
    function dragstarted(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }
    
    function dragged(event: any, d: any) {
      d.fx = event.x;
      d.fy = event.y;
    }
    
    function dragended(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }
    
  }, [graphData]);
  
  const getNodeColor = (type: string): string => {
    const colors: { [key: string]: string } = {
      'Person': '#ff6b6b',
      'Place': '#4ecdc4',
      'Event': '#45b7d1',
      'Concept': '#96ceb4',
      'Object': '#ffeaa7'
    };
    return colors[type] || '#ddd';
  };
  
  return (
    <div className="entity-graph">
      <svg ref={svgRef} width={800} height={600} />
    </div>
  );
};
```

**Phase 5 Deliverables**:

- Interactive graph visualization
- Concept relationship maps
- Analytics dashboard
- Network analysis tools

## Phase 6: Multi-Text Expansion (Months 11-12)

**Goal**: Extend to multiple sacred texts with cross-text analysis

### 6.1 Multi-Text Knowledge Graph

Extend schema for multiple texts:

```json
{
  "@context": {
    "ramayana": "http://example.org/ramayana/",
    "gita": "http://example.org/gita/",
    "mahabharata": "http://example.org/mahabharata/"
  },
  "@graph": [
    {
      "@id": "ramayana:Rama",
      "@type": "Person",
      "rdfs:label": "Rama",
      "owl:sameAs": "gita:Krishna",
      "hasIncarnation": "gita:Krishna"
    }
  ]
}
```

### 6.2 Cross-Text Analysis Service

Create service for cross-text comparisons:

```python
# api/services/cross_text_service.py
class CrossTextAnalysisService:
    """Service for analyzing entities and concepts across multiple texts"""
    
    def __init__(self, kg_service: KnowledgeGraphService):
        self.kg_service = kg_service
    
    def find_equivalent_entities(self, entity_id: str) -> List[str]:
        """Find equivalent entities across texts"""
        entity = self.kg_service.get_entity(entity_id)
        
        # Look for owl:sameAs relationships
        same_as_rels = self.kg_service.get_relationships_by_predicate(entity_id, 'owl:sameAs')
        
        return [rel.object_id for rel in same_as_rels]
    
    def compare_concepts_across_texts(self, concept: str) -> Dict[str, Any]:
        """Compare how a concept appears across different texts"""
        results = {}
        
        # Find all text units mentioning this concept
        for text_id in ['ramayana', 'gita', 'mahabharata']:
            text_units = self.kg_service.get_text_units_by_concept(text_id, concept)
            results[text_id] = {
                'count': len(text_units),
                'examples': text_units[:5],  # Top 5 examples
                'contexts': [unit.get_entity_context() for unit in text_units[:3]]
            }
        
        return results
    
    def trace_entity_evolution(self, entity_id: str) -> Dict[str, Any]:
        """Trace how an entity is portrayed across texts"""
        entity = self.kg_service.get_entity(entity_id)
        evolution = {}
        
        # Get mentions across all texts
        for text_id in self.kg_service.get_available_texts():
            mentions = self.kg_service.get_entity_mentions_in_text(entity_id, text_id)
            
            if mentions:
                evolution[text_id] = {
                    'mention_count': len(mentions),
                    'key_relationships': self._get_key_relationships_in_text(entity_id, text_id),
                    'character_development': self._analyze_character_development(entity_id, text_id)
                }
        
        return evolution
```

**Phase 6 Deliverables**:

- Multi-text knowledge graph
- Cross-text entity resolution
- Comparative analysis tools
- Universal entity browser

## Implementation Timeline

### Quick Wins (Weeks 1-4)

1. JSON-LD schema with 20 core entities
2. Basic KG models and database schema
3. Simple entity extraction for character names
4. Enhanced text unit responses with entity mentions

### Month 1-2 Milestones

1. Complete KG foundation with 50+ entities
2. Entity extraction pipeline
3. Basic semantic annotations
4. KG API endpoints

### Month 3-4 Milestones

1. Integrated KG service
2. Enhanced search with entity filtering
3. 100+ entities with relationships
4. Basic graph visualization

### Month 5-6 Milestones

1. Semantic search with vector embeddings
2. Unified search interface
3. Performance optimization
4. Advanced search UI

### Month 7-8 Milestones

1. KG-enhanced RAG system
2. Intelligent chat with entity context
3. Citation generation
4. Context-aware responses

### Month 9-10 Milestones

1. Interactive graph visualization
2. Analytics dashboard
3. Relationship analysis tools
4. Export capabilities

### Month 11-12 Milestones

1. Multi-text support (Bhagavad Gita)
2. Cross-text analysis
3. Comparative study tools
4. Performance optimization

## Success Metrics

### Technical Metrics

- **Entity Recognition**: >90% accuracy for character names
- **Search Performance**: <200ms for semantic search
- **Graph Queries**: <100ms for entity relationships
- **API Response Time**: <500ms for complex KG queries

### User Experience Metrics

- **Search Relevance**: >85% user satisfaction
- **AI Response Quality**: >80% helpful responses
- **Feature Adoption**: >60% users try KG features
- **Session Duration**: 50% increase in engagement

### Content Metrics

- **Entity Coverage**: 95% of major characters mapped
- **Relationship Accuracy**: >95% verified relationships
- **Cross-References**: 100% major entities cross-referenced
- **Multilingual Support**: Sanskrit and English labels

## Risk Mitigation

### Technical Risks

1. **Performance**: Incremental optimization, caching strategies
2. **Data Quality**: Expert validation, community review
3. **Complexity**: Modular architecture, comprehensive testing
4. **Scalability**: Horizontal scaling, database optimization

### Cultural Risks

1. **Accuracy**: Sanskrit scholar review, source validation
2. **Sensitivity**: Community feedback, respectful presentation
3. **Bias**: Diverse perspectives, multiple source validation
4. **Attribution**: Proper source citation, scholar recognition

## Conclusion

This phased implementation plan provides a clear roadmap for integrating knowledge graph capabilities into the Ramayana platform. The approach builds incrementally on the existing strong foundation while adding powerful semantic capabilities that will transform the user experience.

The plan prioritizes:

- **Solid Foundation**: Proper schema design and data modeling
- **Incremental Value**: Each phase delivers usable features
- **Cultural Sensitivity**: Expert review and community involvement
- **Technical Excellence**: Performance, scalability, and maintainability

By following this plan, the platform will evolve from a text search system into a comprehensive knowledge platform that enables deep exploration of Hindu sacred literature through AI-powered semantic analysis.
