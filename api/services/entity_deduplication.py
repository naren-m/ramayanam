"""
Entity Deduplication and Merging Service
Handles consolidation of duplicate entities discovered through different patterns
"""

import sqlite3
import json
import logging
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict
from dataclasses import dataclass
from difflib import SequenceMatcher
import re

@dataclass
class DuplicateCandidate:
    """Candidate pair of potentially duplicate entities"""
    entity1_id: str
    entity2_id: str
    similarity_score: float
    similarity_type: str  # 'name', 'pattern', 'context'
    confidence: float

@dataclass
class MergeProposal:
    """Proposal for merging entities"""
    primary_entity_id: str
    duplicate_entity_ids: List[str]
    merged_labels: Dict[str, str]
    merged_properties: Dict[str, Any]
    total_mentions: int
    confidence: float

class EntityDeduplicationService:
    """Service for identifying and merging duplicate entities"""
    
    def __init__(self, db_path: str = "data/db/ramayanam.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Similarity thresholds
        self.name_similarity_threshold = 0.8
        self.context_similarity_threshold = 0.7
        self.minimum_merge_confidence = 0.75
        
    def get_connection(self):
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def find_duplicate_candidates(self) -> List[DuplicateCandidate]:
        """Find potential duplicate entities using multiple strategies"""
        self.logger.info("Starting duplicate entity detection")
        
        candidates = []
        
        with self.get_connection() as conn:
            entities = conn.execute("""
                SELECT kg_id, entity_type, labels, properties 
                FROM kg_entities
            """).fetchall()
        
        entities_list = list(entities)
        
        # Compare each entity with every other entity
        for i in range(len(entities_list)):
            for j in range(i + 1, len(entities_list)):
                entity1 = entities_list[i]
                entity2 = entities_list[j]
                
                # Only compare entities of the same type
                if entity1['entity_type'] != entity2['entity_type']:
                    continue
                
                candidate = self._analyze_entity_similarity(entity1, entity2)
                if candidate and candidate.confidence >= self.minimum_merge_confidence:
                    candidates.append(candidate)
        
        self.logger.info(f"Found {len(candidates)} duplicate candidates")
        return candidates
    
    def _analyze_entity_similarity(self, entity1, entity2) -> Optional[DuplicateCandidate]:
        """Analyze similarity between two entities"""
        entity1_id = self._extract_entity_id(entity1['kg_id'])
        entity2_id = self._extract_entity_id(entity2['kg_id'])
        
        labels1 = json.loads(entity1['labels'])
        labels2 = json.loads(entity2['labels'])
        properties1 = json.loads(entity1['properties'])
        properties2 = json.loads(entity2['properties'])
        
        similarities = []
        
        # Name similarity (primary labels)
        name_sim = self._calculate_name_similarity(labels1, labels2)
        if name_sim > 0:
            similarities.append(('name', name_sim))
        
        # Epithet/alternative name similarity
        epithet_sim = self._calculate_epithet_similarity(properties1, properties2)
        if epithet_sim > 0:
            similarities.append(('epithet', epithet_sim))
        
        # Context similarity (context words)
        context_sim = self._calculate_context_similarity(properties1, properties2)
        if context_sim > 0:
            similarities.append(('context', context_sim))
        
        if not similarities:
            return None
        
        # Calculate overall confidence
        max_similarity = max(sim[1] for sim in similarities)
        avg_similarity = sum(sim[1] for sim in similarities) / len(similarities)
        confidence = (max_similarity * 0.7) + (avg_similarity * 0.3)
        
        if confidence >= self.minimum_merge_confidence:
            best_sim_type = max(similarities, key=lambda x: x[1])[0]
            
            return DuplicateCandidate(
                entity1_id=entity1_id,
                entity2_id=entity2_id,
                similarity_score=max_similarity,
                similarity_type=best_sim_type,
                confidence=confidence
            )
        
        return None
    
    def _extract_entity_id(self, kg_id: str) -> str:
        """Extract entity ID from KG URI"""
        return kg_id.split('/')[-1]
    
    def _calculate_name_similarity(self, labels1: Dict, labels2: Dict) -> float:
        """Calculate similarity between entity names"""
        similarities = []
        
        # Compare English names
        if 'en' in labels1 and 'en' in labels2:
            en_sim = SequenceMatcher(None, labels1['en'].lower(), labels2['en'].lower()).ratio()
            similarities.append(en_sim)
        
        # Compare Sanskrit names
        if 'sa' in labels1 and 'sa' in labels2:
            sa_sim = SequenceMatcher(None, labels1['sa'], labels2['sa']).ratio()
            similarities.append(sa_sim)
        
        return max(similarities) if similarities else 0.0
    
    def _calculate_epithet_similarity(self, props1: Dict, props2: Dict) -> float:
        """Calculate similarity between epithets and alternative names"""
        epithets1 = set(props1.get('epithets', []) + props1.get('alternative_names', []))
        epithets2 = set(props2.get('epithets', []) + props2.get('alternative_names', []))
        
        if not epithets1 or not epithets2:
            return 0.0
        
        # Check for exact matches
        intersection = epithets1.intersection(epithets2)
        if intersection:
            return len(intersection) / min(len(epithets1), len(epithets2))
        
        # Check for partial matches
        max_sim = 0.0
        for e1 in epithets1:
            for e2 in epithets2:
                sim = SequenceMatcher(None, e1.lower(), e2.lower()).ratio()
                max_sim = max(max_sim, sim)
        
        return max_sim if max_sim > 0.8 else 0.0
    
    def _calculate_context_similarity(self, props1: Dict, props2: Dict) -> float:
        """Calculate similarity between context words"""
        context1 = set(props1.get('context_words', []))
        context2 = set(props2.get('context_words', []))
        
        if not context1 or not context2:
            return 0.0
        
        intersection = context1.intersection(context2)
        union = context1.union(context2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def create_merge_proposals(self, candidates: List[DuplicateCandidate]) -> List[MergeProposal]:
        """Create merge proposals from duplicate candidates"""
        self.logger.info("Creating merge proposals")
        
        # Group candidates by connected components
        entity_groups = self._find_connected_components(candidates)
        
        proposals = []
        with self.get_connection() as conn:
            for group in entity_groups:
                if len(group) < 2:
                    continue
                
                proposal = self._create_merge_proposal_for_group(conn, group, candidates)
                if proposal:
                    proposals.append(proposal)
        
        self.logger.info(f"Created {len(proposals)} merge proposals")
        return proposals
    
    def _find_connected_components(self, candidates: List[DuplicateCandidate]) -> List[List[str]]:
        """Find connected components of entities that should be merged together"""
        # Build adjacency list
        graph = defaultdict(set)
        all_entities = set()
        
        for candidate in candidates:
            graph[candidate.entity1_id].add(candidate.entity2_id)
            graph[candidate.entity2_id].add(candidate.entity1_id)
            all_entities.add(candidate.entity1_id)
            all_entities.add(candidate.entity2_id)
        
        # Find connected components using DFS
        visited = set()
        components = []
        
        for entity in all_entities:
            if entity not in visited:
                component = []
                self._dfs(entity, graph, visited, component)
                if len(component) > 1:
                    components.append(component)
        
        return components
    
    def _dfs(self, entity: str, graph: Dict[str, Set[str]], visited: Set[str], component: List[str]):
        """Depth-first search for connected components"""
        visited.add(entity)
        component.append(entity)
        
        for neighbor in graph[entity]:
            if neighbor not in visited:
                self._dfs(neighbor, graph, visited, component)
    
    def _create_merge_proposal_for_group(self, conn, entity_group: List[str], 
                                       candidates: List[DuplicateCandidate]) -> Optional[MergeProposal]:
        """Create a merge proposal for a group of entities"""
        # Get entity data
        entity_data = {}
        mention_counts = {}
        
        for entity_id in entity_group:
            kg_id = f"http://ramayanam.hanuma.com/entity/{entity_id}"
            
            entity_row = conn.execute("""
                SELECT kg_id, entity_type, labels, properties 
                FROM kg_entities WHERE kg_id = ?
            """, (kg_id,)).fetchone()
            
            if entity_row:
                entity_data[entity_id] = entity_row
                
                # Get mention count
                mention_count = conn.execute("""
                    SELECT COUNT(*) as count FROM text_entity_mentions 
                    WHERE entity_id = ?
                """, (entity_id,)).fetchone()['count']
                
                mention_counts[entity_id] = mention_count
        
        if not entity_data:
            return None
        
        # Choose primary entity (highest mention count)
        primary_entity_id = max(mention_counts.keys(), key=lambda x: mention_counts[x])
        duplicate_ids = [eid for eid in entity_group if eid != primary_entity_id]
        
        # Merge labels and properties
        merged_labels, merged_properties = self._merge_entity_data(entity_data, primary_entity_id)
        
        # Calculate confidence
        group_candidates = [c for c in candidates if c.entity1_id in entity_group and c.entity2_id in entity_group]
        avg_confidence = sum(c.confidence for c in group_candidates) / len(group_candidates) if group_candidates else 0.8
        
        return MergeProposal(
            primary_entity_id=primary_entity_id,
            duplicate_entity_ids=duplicate_ids,
            merged_labels=merged_labels,
            merged_properties=merged_properties,
            total_mentions=sum(mention_counts.values()),
            confidence=avg_confidence
        )
    
    def _merge_entity_data(self, entity_data: Dict[str, Any], primary_id: str) -> Tuple[Dict[str, str], Dict[str, Any]]:
        """Merge labels and properties from multiple entities"""
        primary_entity = entity_data[primary_id]
        primary_labels = json.loads(primary_entity['labels'])
        primary_properties = json.loads(primary_entity['properties'])
        
        merged_labels = primary_labels.copy()
        merged_properties = primary_properties.copy()
        
        # Collect all alternative names and epithets
        all_epithets = set(merged_properties.get('epithets', []))
        all_alt_names = set(merged_properties.get('alternative_names', []))
        all_context_words = set(merged_properties.get('context_words', []))
        
        for entity_id, entity_row in entity_data.items():
            if entity_id == primary_id:
                continue
            
            labels = json.loads(entity_row['labels'])
            properties = json.loads(entity_row['properties'])
            
            # Add alternative labels
            for lang, name in labels.items():
                if lang not in merged_labels and name:
                    merged_labels[lang] = name
            
            # Merge epithets and alternative names
            all_epithets.update(properties.get('epithets', []))
            all_alt_names.update(properties.get('alternative_names', []))
            all_context_words.update(properties.get('context_words', []))
        
        # Update merged properties
        merged_properties['epithets'] = list(all_epithets)
        merged_properties['alternative_names'] = list(all_alt_names)
        merged_properties['context_words'] = list(all_context_words)
        merged_properties['merged_from'] = list(entity_data.keys())
        
        return merged_labels, merged_properties
    
    def execute_merge_proposal(self, proposal: MergeProposal) -> bool:
        """Execute a merge proposal"""
        self.logger.info(f"Executing merge: {proposal.primary_entity_id} <- {proposal.duplicate_entity_ids}")
        
        with self.get_connection() as conn:
            try:
                # Update primary entity with merged data
                primary_kg_id = f"http://ramayanam.hanuma.com/entity/{proposal.primary_entity_id}"
                
                conn.execute("""
                    UPDATE kg_entities 
                    SET labels = ?, properties = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE kg_id = ?
                """, (
                    json.dumps(proposal.merged_labels),
                    json.dumps(proposal.merged_properties),
                    primary_kg_id
                ))
                
                # Transfer mentions from duplicate entities to primary
                for duplicate_id in proposal.duplicate_entity_ids:
                    conn.execute("""
                        UPDATE text_entity_mentions 
                        SET entity_id = ? 
                        WHERE entity_id = ?
                    """, (proposal.primary_entity_id, duplicate_id))
                
                # Delete duplicate entities
                for duplicate_id in proposal.duplicate_entity_ids:
                    duplicate_kg_id = f"http://ramayanam.hanuma.com/entity/{duplicate_id}"
                    conn.execute("DELETE FROM kg_entities WHERE kg_id = ?", (duplicate_kg_id,))
                
                conn.commit()
                self.logger.info(f"Successfully merged {len(proposal.duplicate_entity_ids)} entities into {proposal.primary_entity_id}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to execute merge proposal: {e}")
                conn.rollback()
                return False
    
    def run_deduplication_process(self, auto_merge_threshold: float = 0.9) -> Dict[str, Any]:
        """Run the complete deduplication process"""
        self.logger.info("Starting entity deduplication process")
        
        # Find duplicates
        candidates = self.find_duplicate_candidates()
        
        # Create merge proposals
        proposals = self.create_merge_proposals(candidates)
        
        # Auto-merge high confidence proposals
        auto_merged = 0
        manual_review = []
        
        for proposal in proposals:
            if proposal.confidence >= auto_merge_threshold:
                if self.execute_merge_proposal(proposal):
                    auto_merged += 1
            else:
                manual_review.append(proposal)
        
        results = {
            'candidates_found': len(candidates),
            'proposals_created': len(proposals),
            'auto_merged': auto_merged,
            'manual_review_needed': len(manual_review),
            'manual_review_proposals': manual_review
        }
        
        self.logger.info(f"Deduplication complete: {auto_merged} auto-merged, {len(manual_review)} need manual review")
        return results

def run_deduplication():
    """Main function to run entity deduplication"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    service = EntityDeduplicationService()
    results = service.run_deduplication_process()
    
    print("🔄 Entity Deduplication Results")
    print("=" * 50)
    print(f"Duplicate candidates found: {results['candidates_found']}")
    print(f"Merge proposals created: {results['proposals_created']}")
    print(f"Auto-merged entities: {results['auto_merged']}")
    print(f"Manual review needed: {results['manual_review_needed']}")
    
    if results['manual_review_proposals']:
        print("\n📋 Manual Review Proposals:")
        for i, proposal in enumerate(results['manual_review_proposals'], 1):
            print(f"{i}. {proposal.primary_entity_id} <- {proposal.duplicate_entity_ids}")
            print(f"   Confidence: {proposal.confidence:.2f}, Total mentions: {proposal.total_mentions}")
    
    return results

if __name__ == "__main__":
    run_deduplication()