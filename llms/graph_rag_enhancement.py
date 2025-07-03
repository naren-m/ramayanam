#!/usr/bin/env python3
"""
Graph RAG Enhancement for Ramayanam System
Implements Knowledge Graph extraction and traversal for improved RAG
"""

import logging
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
import networkx as nx
from py2neo import Graph, Node, Relationship
import spacy
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class RamayanamEntity:
    """Represents an entity in Ramayanam"""
    name: str
    type: str  # person, place, event, concept
    attributes: Dict[str, str]
    
@dataclass
class RamayanamRelation:
    """Represents a relationship between entities"""
    source: str
    target: str
    relation_type: str
    attributes: Dict[str, str]

class RamayanamKnowledgeGraphBuilder:
    """Builds a knowledge graph from Ramayanam text"""
    
    def __init__(self):
        # Load spaCy model for NER
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            logger.warning("spaCy model not found, using basic extraction")
            self.nlp = None
            
        # Define Ramayanam-specific entities
        self.characters = {
            "राम", "सीता", "लक्ष्मण", "भरत", "शत्रुघ्न", "दशरथ", "कौसल्या",
            "हनुमान", "सुग्रीव", "रावण", "विभीषण", "वाली", "अंगद",
            "Rama", "Sita", "Lakshmana", "Bharata", "Dasharatha", "Hanuman"
        }
        
        self.places = {
            "अयोध्या", "लंका", "किष्किन्धा", "पंचवटी", "चित्रकूट", "मिथिला",
            "Ayodhya", "Lanka", "Kishkindha", "Panchavati", "Chitrakuta"
        }
        
        self.relationships = {
            "father_of": ["पिता", "father", "जनक"],
            "mother_of": ["माता", "mother", "जननी"],
            "brother_of": ["भ्राता", "brother", "भाई"],
            "wife_of": ["पत्नी", "wife", "भार्या"],
            "devotee_of": ["भक्त", "devotee", "सेवक"],
            "enemy_of": ["शत्रु", "enemy", "विरोधी"]
        }
        
    def extract_entities_from_sloka(self, sanskrit_text: str, translation: str = "") -> List[RamayanamEntity]:
        """Extract entities from a sloka"""
        entities = []
        
        # Extract from Sanskrit text
        for char in self.characters:
            if char in sanskrit_text:
                entities.append(RamayanamEntity(
                    name=char,
                    type="character",
                    attributes={"source": "sanskrit"}
                ))
                
        for place in self.places:
            if place in sanskrit_text:
                entities.append(RamayanamEntity(
                    name=place,
                    type="place",
                    attributes={"source": "sanskrit"}
                ))
                
        # If translation available, extract from there too
        if translation and self.nlp:
            doc = self.nlp(translation)
            for ent in doc.ents:
                if ent.label_ in ["PERSON", "LOC", "GPE"]:
                    entities.append(RamayanamEntity(
                        name=ent.text,
                        type="character" if ent.label_ == "PERSON" else "place",
                        attributes={"source": "translation", "label": ent.label_}
                    ))
                    
        return entities
    
    def extract_relations_from_text(self, text: str, entities: List[RamayanamEntity]) -> List[RamayanamRelation]:
        """Extract relationships between entities"""
        relations = []
        entity_names = {e.name for e in entities}
        
        # Simple pattern matching for relationships
        for rel_type, patterns in self.relationships.items():
            for pattern in patterns:
                if pattern in text:
                    # Find entities that might be related
                    # This is simplified - in production, use dependency parsing
                    for e1 in entity_names:
                        for e2 in entity_names:
                            if e1 != e2 and e1 in text and e2 in text:
                                relations.append(RamayanamRelation(
                                    source=e1,
                                    target=e2,
                                    relation_type=rel_type,
                                    attributes={"pattern": pattern}
                                ))
                                
        return relations

class GraphRAGRetriever:
    """Enhanced retriever using Knowledge Graph + Vector Search"""
    
    def __init__(self, neo4j_uri: str = "bolt://localhost:7687", 
                 neo4j_user: str = "neo4j", 
                 neo4j_password: str = "password"):
        """Initialize graph database connection"""
        try:
            self.graph = Graph(neo4j_uri, auth=(neo4j_user, neo4j_password))
            self.connected = True
        except:
            logger.warning("Could not connect to Neo4j, using in-memory graph")
            self.graph = nx.DiGraph()
            self.connected = False
            
    def retrieve_with_graph_expansion(self, 
                                    initial_nodes: List[str], 
                                    max_hops: int = 2,
                                    relationship_types: Optional[List[str]] = None) -> Dict:
        """
        Expand from initial nodes (from vector search) using graph traversal
        
        This implements the core Graph RAG pattern:
        1. Start with nodes from vector search
        2. Traverse graph to find related context
        3. Return expanded context
        """
        
        if self.connected:
            # Neo4j Cypher query for graph traversal
            query = """
            MATCH path = (start)-[*1..%d]-(connected)
            WHERE start.name IN $initial_nodes
            %s
            RETURN DISTINCT connected, relationships(path) as rels
            LIMIT 50
            """
            
            rel_filter = ""
            if relationship_types:
                rel_filter = f"AND ALL(r IN relationships(path) WHERE type(r) IN {relationship_types})"
                
            results = self.graph.run(
                query % (max_hops, rel_filter),
                initial_nodes=initial_nodes
            ).data()
            
            expanded_context = {
                "nodes": [],
                "relationships": []
            }
            
            for record in results:
                node = record["connected"]
                expanded_context["nodes"].append({
                    "name": node["name"],
                    "type": node["type"],
                    "content": node.get("content", "")
                })
                
                for rel in record["rels"]:
                    expanded_context["relationships"].append({
                        "type": type(rel).__name__,
                        "source": rel.start_node["name"],
                        "target": rel.end_node["name"]
                    })
                    
            return expanded_context
            
        else:
            # Fallback to NetworkX in-memory traversal
            expanded_nodes = set(initial_nodes)
            
            for hop in range(max_hops):
                new_nodes = set()
                for node in expanded_nodes:
                    if node in self.graph:
                        # Get neighbors
                        neighbors = list(self.graph.neighbors(node))
                        new_nodes.update(neighbors)
                expanded_nodes.update(new_nodes)
                
            return {
                "nodes": [{"name": n} for n in expanded_nodes],
                "relationships": []
            }
    
    def get_subgraph_context(self, central_node: str, radius: int = 2) -> nx.Graph:
        """Get subgraph around a central node"""
        if not self.connected:
            # Use NetworkX
            if central_node in self.graph:
                # Get all nodes within radius
                subgraph_nodes = nx.single_source_shortest_path_length(
                    self.graph, central_node, cutoff=radius
                ).keys()
                return self.graph.subgraph(subgraph_nodes)
        return nx.Graph()

class RamayanamGraphRAG:
    """Main Graph RAG implementation for Ramayanam"""
    
    def __init__(self, vector_store, knowledge_graph: GraphRAGRetriever):
        self.vector_store = vector_store
        self.kg = knowledge_graph
        self.builder = RamayanamKnowledgeGraphBuilder()
        
    def enhanced_search(self, 
                       query: str, 
                       top_k_vector: int = 5,
                       graph_expansion_hops: int = 2) -> Dict:
        """
        Perform Graph RAG search:
        1. Vector search for initial nodes
        2. Graph expansion for additional context
        3. Combine and rank results
        """
        
        # Step 1: Vector search
        vector_results = self.vector_store.search(query, top_k_vector)
        
        # Extract entities from vector results
        initial_entities = set()
        for result in vector_results:
            entities = self.builder.extract_entities_from_sloka(
                result.sanskrit_text,
                result.translation
            )
            initial_entities.update([e.name for e in entities])
            
        # Step 2: Graph expansion
        graph_context = self.kg.retrieve_with_graph_expansion(
            list(initial_entities),
            max_hops=graph_expansion_hops
        )
        
        # Step 3: Combine results
        combined_results = {
            "vector_results": vector_results,
            "graph_expansion": graph_context,
            "total_context_size": len(vector_results) + len(graph_context["nodes"])
        }
        
        return combined_results
    
    def build_knowledge_graph_from_corpus(self, slokas: List):
        """Build knowledge graph from Ramayanam corpus"""
        logger.info("Building Ramayanam Knowledge Graph...")
        
        all_entities = []
        all_relations = []
        
        for sloka in slokas:
            # Extract entities
            entities = self.builder.extract_entities_from_sloka(
                sloka.sanskrit_text,
                sloka.translation
            )
            all_entities.extend(entities)
            
            # Extract relations
            combined_text = f"{sloka.sanskrit_text} {sloka.translation}"
            relations = self.builder.extract_relations_from_text(
                combined_text, entities
            )
            all_relations.extend(relations)
            
        # Create graph
        if self.kg.connected:
            # Use Neo4j
            for entity in all_entities:
                node = Node(entity.type, name=entity.name, **entity.attributes)
                self.kg.graph.merge(node, entity.type, "name")
                
            for relation in all_relations:
                source = self.kg.graph.nodes.match(name=relation.source).first()
                target = self.kg.graph.nodes.match(name=relation.target).first()
                if source and target:
                    rel = Relationship(
                        source, relation.relation_type, target,
                        **relation.attributes
                    )
                    self.kg.graph.merge(rel)
        else:
            # Use NetworkX
            for entity in all_entities:
                self.kg.graph.add_node(entity.name, **entity.attributes)
                
            for relation in all_relations:
                self.kg.graph.add_edge(
                    relation.source, 
                    relation.target,
                    type=relation.relation_type,
                    **relation.attributes
                )
                
        logger.info(f"Knowledge graph built with {len(all_entities)} entities "
                   f"and {len(all_relations)} relations")

# Example usage
if __name__ == "__main__":
    # This would integrate with the existing RamayanamRAGSystem
    print("Ramayanam Graph RAG Enhancement")
    print("=" * 50)
    print("\nThis module adds Knowledge Graph capabilities to the RAG system:")
    print("- Entity extraction (characters, places, events)")
    print("- Relationship extraction") 
    print("- Graph-based context expansion")
    print("- Combined vector + graph retrieval")
    print("\nBenefits (as per the talk):")
    print("- 3x higher accuracy")
    print("- Easier debugging and development")
    print("- Better explainability")