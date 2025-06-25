"""
Knowledge Graph Models for Ramayana Entity Extraction

This module defines the data models for representing knowledge graph entities,
relationships, and semantic annotations in the Ramayana corpus.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class EntityType(Enum):
    """Types of entities in the knowledge graph"""
    PERSON = "Person"
    PLACE = "Place"
    EVENT = "Event"
    OBJECT = "Object"
    CONCEPT = "Concept"


@dataclass
class KGEntity:
    """Knowledge Graph Entity representation"""
    kg_id: str  # URI identifier like http://ramayanam.hanuma.com/entity/rama
    entity_type: EntityType
    labels: Dict[str, str]  # Language -> label mapping {"en": "Rama", "sa": "राम"}
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def serialize(self) -> Dict[str, Any]:
        """Serialize entity for JSON output"""
        return {
            "kg_id": self.kg_id,
            "entity_type": self.entity_type.value,
            "labels": self.labels,
            "properties": self.properties
        }


@dataclass
class KGRelationship:
    """Knowledge Graph Relationship representation"""
    subject_id: str  # Subject entity ID
    predicate: str   # Relationship type (hasSpouse, devoteeOf, etc.)
    object_id: str   # Object entity ID
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def serialize(self) -> Dict[str, Any]:
        """Serialize relationship for JSON output"""
        return {
            "subject_id": self.subject_id,
            "predicate": self.predicate,
            "object_id": self.object_id,
            "metadata": self.metadata
        }


@dataclass
class SemanticAnnotation:
    """Semantic annotation linking text spans to entities"""
    text_unit_id: str  # ID of the text unit (sloka)
    entity_id: str     # ID of the mentioned entity
    span_start: int    # Start position in text
    span_end: int      # End position in text
    confidence: float = 1.0  # Confidence score
    
    def serialize(self) -> Dict[str, Any]:
        """Serialize annotation for JSON output"""
        return {
            "text_unit_id": self.text_unit_id,
            "entity_id": self.entity_id,
            "span_start": self.span_start,
            "span_end": self.span_end,
            "confidence": self.confidence
        }


# Relationship predicates commonly used in Ramayana
class Predicates:
    """Standard predicates for Ramayana relationships"""
    HAS_SPOUSE = "hasSpouse"
    HAS_PARENT = "hasParent"
    HAS_CHILD = "hasChild"
    HAS_SIBLING = "hasSibling"
    DEVOTEE_OF = "devoteeOf"
    RULES = "rules"
    LIVES_IN = "livesIn"
    BORN_IN = "bornIn"
    TRAVELS_TO = "travelsTo"
    MENTIONED_IN = "mentionedIn"
    EMBODIES = "embodies"
    EXEMPLIFIES = "exemplifies"